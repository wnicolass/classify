import os
import httpx
from typing import Annotated
from urllib.parse import quote_plus as quote
from dotenv import (
    load_dotenv,
    find_dotenv
)
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import (
    APIRouter,
    Request,
    Depends,
    Response,
    responses,
    status,
    HTTPException
)
from jose import jwt
from services import user_service
from common.auth import (
    get_session,
    requires_unauthentication,
    ExternalLoginError,
    set_current_user,
    hash_sub
)
from common.fastapi_utils import (
    get_db_session,
    form_field_as_str
)
from common.utils import (
    is_ascii,
    generate_csrf_token,
    generate_nonce
)
from models.user import OpenIdConnectTokens

load_dotenv(find_dotenv())
router = APIRouter()

MICROSOFT_CLIENT_ID = os.getenv('MICROSOFT_CLIENT_ID')
MICROSOFT_REDIRECT_URI = os.getenv('MICROSOFT_REDIRECT_URI')
MICROSOFT_CONFIGURATION_DOCUMENT_URL = os.getenv('MICROSOFT_CONFIGURATION_DOCUMENT_URL')
MICROSOFT_RESPONSE_MODE = os.getenv('MICROSOFT_RESPONSE_MODE')
MICROSOFT_GRANT_TYPE = os.getenv('MICROSOFT_GRANT_TYPE')
MICROSOFT_TOKEN_SECRET = os.getenv('MICROSOFT_TOKEN_SECRET')
MICROSOFT_HASH_SECRET = os.getenv('MICROSOFT_HASH_SECRET')

@router.get('/auth/microsoft', dependencies = [Depends(requires_unauthentication)])
async def microsoft_external_login(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    response: Response
):
    ext_provider = await user_service.get_external_provider_by_id(
        session, 
        ext_provider_id = 2
    )

    if not ext_provider:
        raise ExternalLoginError('Unknown external provider')
    url = await create_auth_request(request, session)

    return responses.RedirectResponse(url = url)

async def create_auth_request(
    request: Request,
    session: AsyncSession
) -> str:
    csrf_token = generate_csrf_token()
    nonce = generate_nonce(64)
    await user_service.save_oauth_tokens(csrf_token, nonce, session)
    query_params = {
        'response_type': 'code id_token',
        'client_id': MICROSOFT_CLIENT_ID,
        'response_mode': MICROSOFT_RESPONSE_MODE,
        'redirect_uri': MICROSOFT_REDIRECT_URI,
        'scope': 'openid profile email',
        'state': csrf_token,
        'nonce': nonce
    }

    """
        Since URLs are limited to a specific set of characters, 
        any characters that are not allowed in a URL (such as spaces 
        or non-ASCII characters) must be encoded.
        The 'quote()' function encodes a string by replacing any
        characters that are not allowed in a URL with their percent-encoded
        representation (e.g. 'hello world!' -> 'hello+world%21').
    """
    query_string = '&'.join(
        f'{param}={quote(value)}' for param, value in query_params.items()
    )

    discovery_document = await get_discovery_document(httpx.AsyncClient)
    microsoft_base_uri = discovery_document['authorization_endpoint']

    return f'{microsoft_base_uri}?{query_string}'

@router.post(
    '/auth/microsoft/continue', 
    dependencies = [Depends(requires_unauthentication)]
)
async def microsoft_external_login_response(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    request: Request
):
    form_data = await request.form()
    state = form_field_as_str(form_data, 'state')
    code = form_field_as_str(form_data, 'code')
    
    # Validate state token immediately
    validation_tokens = await user_service.get_oauth_tokens(state, session)
    
    http_session = httpx.AsyncClient
    tokens = await exchange_code_for_tokens(code, http_session)
    
    decoded_id_token = await validate_and_decode_token(
        http_session, 
        tokens,
        validation_tokens,
        session
    )
    
    if decoded_id_token:
        await authenticate_user(decoded_id_token, session)

    return responses.RedirectResponse(url = '/', status_code = status.HTTP_302_FOUND)

async def validate_and_decode_token(
    client: httpx.AsyncClient,
    tokens: dict,
    validation_tokens: OpenIdConnectTokens,
    session: AsyncSession
) -> dict:
    discovery_document = await get_discovery_document(client)
    microsoft_jwks_uri = discovery_document['jwks_uri']
    microsoft_issuer: str = discovery_document['issuer']

    async with client() as async_client:
        res = await async_client.get(microsoft_jwks_uri)
        key = res.json()

        algorithm = jwt.get_unverified_header(tokens['id_token']).get('alg')

        decoded_token = jwt.decode(
            token = tokens['id_token'],
            key = key,
            algorithms = algorithm,
            audience = MICROSOFT_CLIENT_ID,
            access_token = tokens['access_token']
        )

        microsoft_issuer = microsoft_issuer.replace(
            '{tenantid}', 
            decoded_token['tid']
        )
        
        issuer = decoded_token['iss']
        if issuer != microsoft_issuer:
            raise ExternalLoginError(f'Invalid token issuer {issuer}')
        
        expected_nonce = validation_tokens.nonce
        received_nonce = decoded_token['nonce']
        if received_nonce != expected_nonce:
            raise ExternalLoginError(f'Invalid or missing nonce: {received_nonce}')
        await user_service.delete_token_instance(validation_tokens, session)

        sub = decoded_token['sub']
        if len(sub) > 255 or not is_ascii(sub):
            raise ExternalLoginError(f'Invalid sub: {sub}')
        
        return {
            'sub': sub,
            'email_address': decoded_token['email'],
            'username': decoded_token['name']
        }

async def exchange_code_for_tokens(code: str, client: httpx.AsyncClient):
    discovery_document = await get_discovery_document(client)
    token_endpoint = discovery_document['token_endpoint']

    request_body = {
        'code': code,
        'client_id': MICROSOFT_CLIENT_ID,
        'client_secret': MICROSOFT_TOKEN_SECRET,
        'redirect_uri': MICROSOFT_REDIRECT_URI,
        'grant_type': MICROSOFT_GRANT_TYPE
    }

    async with client() as async_client:
        res = await async_client.post(token_endpoint, data = request_body)
        data = res.json()
    
    return {
        'access_token': data['access_token'],
        'expires_in': data['expires_in'],
        'id_token': data['id_token']
    }

async def authenticate_user(id_token: dict, session: AsyncSession):
    user_found_by_email = await user_service.get_user_by_email(id_token['email_address'], session)
    hashed_sub = hash_sub(id_token['sub'], MICROSOFT_HASH_SECRET)
    
    """
        1. User is registed but don't have external login data
        and is trying to sign in with the same email. Create
        external data for that user and then set session cookie.
    """
    user_found_by_sub = await user_service.get_user_by_hashed_sub(hashed_sub, session)
    if user_found_by_email:
        if not user_found_by_sub:
            await user_service.create_user_ext(
                user_found_by_email,
                hashed_sub,
                session
            )
           
        return set_current_user(user_found_by_email.user_id)
    
    """
        2. User was not found by email and not found by external login data.
        Potentially is a new user, so create a new user account, and then associate
        a external data to this created user.
    """
    if not user_found_by_sub:
        new_user = await user_service.create_user(
            username = id_token['username'],
            phone_number = None, 
            birth_date = None, 
            image_url = None,
            is_active = 1,
            session = session
        )
        await user_service.create_user_login_data(
            new_user.user_id,
            id_token['email_address'],
            1,
            session
        )
        await user_service.create_user_ext(
            new_user,
            hashed_sub,
            session,
            external_provider_id = 2
        )
        return set_current_user(new_user.user_id)

async def get_discovery_document(client: httpx.AsyncClient):
    async with client() as async_client:
        res = await async_client.get(MICROSOFT_CONFIGURATION_DOCUMENT_URL)
        return res.json()