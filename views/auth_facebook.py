from datetime import datetime
import os
import httpx
import pkce
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
    hash_sub,
)
from common.fastapi_utils import get_db_session
from common.utils import (
    is_ascii,
    generate_csrf_token,
    generate_nonce,
    generate_query_string
)
load_dotenv(find_dotenv())
router = APIRouter()

FACEBOOK_APP_ID = os.getenv('FACEBOOK_APP_ID')
FACEBOOK_APP_SECRET = os.getenv('FACEBOOK_APP_SECRET')
FACEBOOK_DISCOVERY_DOCUMENT_URL = os.getenv('FACEBOOK_DISCOVERY_DOCUMENT_URL')
FACEBOOK_REDIRECT_URI = os.getenv('FACEBOOK_REDIRECT_URI')
FACEBOOK_TOKEN_ENDPOINT = os.getenv('FACEBOOK_TOKEN_ENDPOINT')
FACEBOOK_HASH_SECRET = os.getenv('FACEBOOK_SECRET')

@router.get('/auth/facebook', dependencies = [Depends(requires_unauthentication)])
async def microsoft_external_login(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_db_session)]
):
    ext_provider = await user_service.get_external_provider_by_id(session, 3)

    if not ext_provider:
        raise ExternalLoginError('Unknown external provider')
    url = await create_auth_request(request)
    return responses.RedirectResponse(url = url)

async def create_auth_request(request: Request):
    csrf_token = generate_csrf_token()
    request.session['state'] = csrf_token

    nonce = generate_nonce(64)
    request.session['nonce'] = nonce

    code_verifier, code_challenge = pkce.generate_pkce_pair()
    request.session['code_verifier'] = code_verifier

    query_params = {
        'response_type': 'code',
        'client_id': FACEBOOK_APP_ID,
        'redirect_uri': FACEBOOK_REDIRECT_URI,
        'scope': 'openid public_profile email',
        'state': csrf_token,
        'nonce': nonce,
        'code_challenge': code_challenge,
        'code_challenge_method': 'S256'
    }

    query_string = generate_query_string(query_params)

    facebook_discovery_doc = await get_discovery_document(httpx.AsyncClient)
    facebook_base_uri = facebook_discovery_doc['authorization_endpoint']

    return f'{facebook_base_uri}?{query_string}'

@router.get('/auth/facebook/continue', dependencies = [Depends(requires_unauthentication)])
async def facebook_external_login_response(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    request: Request,
    state = '',
    code = ''
):
    check_csrf_token(state)
    http_session = httpx.AsyncClient
    tokens = await exchange_code_for_tokens(code, http_session, request)
    decoded_id_token = await validate_and_decode_token(http_session, tokens)
    
    if decoded_id_token:
        await authenticate_user(decoded_id_token, session)

    return responses.RedirectResponse(url = '/')

async def validate_and_decode_token(
    client: httpx.AsyncClient,
    tokens: dict
) -> dict:
    discovery_document = await get_discovery_document(client)
    facebook_jwks_uri = discovery_document['jwks_uri']

    async with client() as async_client:
        res = await async_client.get(facebook_jwks_uri)
        key = res.json()

        algorithm = jwt.get_unverified_header(tokens['id_token']).get('alg')

        decoded_token = jwt.decode(
            token = tokens['id_token'],
            key = key,
            algorithms = algorithm,
            audience = FACEBOOK_APP_ID,
            access_token = tokens['access_token']
        )
        
        issuer = decoded_token['iss']
        if issuer != discovery_document['issuer']:
            raise ExternalLoginError(f'Invalid token issuer {issuer}')
        
        session = get_session()
        expected_nonce = session['nonce']
        received_nonce = decoded_token['nonce']
        if received_nonce != expected_nonce:
            raise ExternalLoginError(f'Invalid or missing nonce: {received_nonce}')
        del session['nonce']

        sub = decoded_token['sub']
        if len(sub) > 255 or not is_ascii(sub):
            raise ExternalLoginError(f'Invalid sub: {sub}')
        
        exp_time = datetime.fromtimestamp(decoded_token['exp'])
        if not datetime.now() < exp_time:
            raise ExternalLoginError(f'Token expired in: {exp_time}')
        
        return {
            'sub': sub,
            'email_address': decoded_token['email'],
            'profile_picture': decoded_token['picture'],
            'username': decoded_token['name']
        }
    
async def authenticate_user(id_token: dict, session: AsyncSession):
    user_found_by_email = await user_service.get_user_by_email(id_token['email_address'], session)
    hashed_sub = hash_sub(id_token['sub'], FACEBOOK_HASH_SECRET)
    
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
                session,
                external_provider_id = 3
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
            image_url = id_token['profile_picture'],
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
            external_provider_id = 3
        )
        return set_current_user(new_user.user_id)

async def exchange_code_for_tokens(
    code: str, 
    client: httpx.AsyncClient, 
    request: Request
) -> dict:
    code_verifier = request.session.get('code_verifier')
    query_params = {
        'client_id': FACEBOOK_APP_ID,
        'code_verifier': code_verifier,
        'redirect_uri': FACEBOOK_REDIRECT_URI,
        'code': code
    }

    query_string = generate_query_string(query_params)

    async with client() as async_client:
        res = await async_client.post(f'{FACEBOOK_TOKEN_ENDPOINT}?{query_string}')
        data = res.json()

    return {
        'access_token': data['access_token'],
        'expires_in': data['expires_in'],
        'id_token': data['id_token']
    }


def check_csrf_token(state: str):
    session = get_session()

    if not (csrf_token := session.get('state')):
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = 'CSRF token not in session for the current request.'
        )
    elif csrf_token != state:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = 'Invalid CSRF token.'
        )

async def get_discovery_document(client: httpx.AsyncClient):
    async with client() as async_client:
        res = await async_client.get(FACEBOOK_DISCOVERY_DOCUMENT_URL)
        return res.json()