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
    hash_google_sub
)
from common.fastapi_utils import get_db_session
from common.utils import (
    is_ascii,
    generate_csrf_token,
    generate_nonce
)

load_dotenv(find_dotenv())
router = APIRouter()

"""
    The server authentication flow below was made
    by following the OpenID Connect (a standard 
    that uses the OAuth 2.0 protocol to provide 
    user authentication and identity information).
    OAuth 2.0 is the protocol that allows the user
    to grant third-applications (e.g. classify) access
    to their resources without sharing their credentials.

    More information:
    https://developers.google.com/identity/openid-connect/openid-connect
    https://openid.net/connect/
    https://auth0.com/intro-to-iam/what-is-oauth-2
"""

GOOGLE_DISCOVERY_DOCUMENT_URL = os.getenv('GOOGLE_DISCOVERY_DOCUMENT_URL')
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_REDIRECT_URI = os.getenv('GOOGLE_REDIRECT_URI')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
GOOGLE_GRANT_TYPE = os.getenv('GOOGLE_GRANT_TYPE')

@router.get('/auth/google', dependencies = [Depends(requires_unauthentication)])
async def google_external_login(
    request: Request, 
    session: Annotated[AsyncSession, Depends(get_db_session)]
):
    ext_provider = await user_service.get_external_provider_by_id(session)

    if not ext_provider:
        raise ExternalLoginError('Unknown external provider')
    url = await create_auth_request(request)
    return responses.RedirectResponse(url = url)

"""
    As the name says, this functions is used to create
    the user authentication request.
    We need a CSRF token, that is used to hold state between
    our app and the user's client and prevent csrf attacks.
    We also need to create a nonce (number used once) to avoid 
    malicious users trying to do a replay attack.

    See:
    https://developers.google.com/identity/openid-connect/openid-connect#createxsrftoken
    https://en.wikipedia.org/wiki/Cross-site_request_forgery
    https://en.wikipedia.org/wiki/Replay_attack
"""
async def create_auth_request(
    request: Request
) -> str:
    csrf_token = generate_csrf_token()
    request.session['state'] = csrf_token

    nonce = generate_nonce(64)
    request.session['nonce'] = nonce
    
    query_params = {
        'response_type': 'code',
        'client_id': GOOGLE_CLIENT_ID,
        'redirect_uri': GOOGLE_REDIRECT_URI,
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
    google_base_uri = discovery_document['authorization_endpoint']

    return f'{google_base_uri}?{query_string}'

@router.get(
    '/auth/google/continue', 
    dependencies = [Depends(requires_unauthentication)]
)
async def google_external_login_response(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    state: str = '',
    code: str = ''
):
    check_csrf_token(state)
    http_session = httpx.AsyncClient
    tokens = await exchange_code_for_tokens(code, http_session)
    decoded_id_token = await validate_and_decode_token(
        http_session, 
        tokens,
    )
    
    if decoded_id_token:
        await authenticate_user(decoded_id_token, session)

    return responses.RedirectResponse(url = '/')

"""
    The following function is used to send
    a post requst in order to get the acess token
    and the id token.
"""
async def exchange_code_for_tokens(code: str, client: httpx.AsyncClient):
    discovery_document = await get_discovery_document(client)
    token_endpoint = discovery_document['token_endpoint']

    request_body = {
        'code': code,
        'client_id': GOOGLE_CLIENT_ID,
        'client_secret': GOOGLE_CLIENT_SECRET,
        'redirect_uri': GOOGLE_REDIRECT_URI,
        'grant_type': GOOGLE_GRANT_TYPE
    }

    async with client() as async_client:
        res = await async_client.post(token_endpoint, data = request_body)
        data = res.json()
    
    return {
        'access_token': data['access_token'],
        'expires_in': data['expires_in'],
        'id_token': data['id_token']
    }

async def validate_and_decode_token(
    client: httpx.AsyncClient,
    tokens: dict
) -> dict:
    discovery_document = await get_discovery_document(client)
    google_jwks_uri = discovery_document['jwks_uri']

    async with client() as async_client:
        res = await async_client.get(google_jwks_uri)
        key = res.json()

        algorithm = jwt.get_unverified_header(tokens['id_token']).get('alg')

        decoded_token = jwt.decode(
            token = tokens['id_token'],
            key = key,
            algorithms = algorithm,
            audience = GOOGLE_CLIENT_ID,
            access_token = tokens['access_token']
        )
        
        issuer = decoded_token['iss']
        if issuer not in [
            'https://accounts.google.com', 
            'accounts.google.com'
        ]:
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
        
        return {
            'sub': sub,
            'email_address': decoded_token['email'],
            'profile_picture': decoded_token['picture'],
            'username': decoded_token['name'],
            'email_verified': decoded_token['email_verified']
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
    
async def authenticate_user(id_token: dict, session: AsyncSession):
    user_found_by_email = await user_service.get_user_by_email(id_token['email_address'], session)
    hashed_sub = hash_google_sub(id_token['sub'])
    
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
            await user_service.update_user_details(
                user = user_found_by_email,
                new_username = '',
                new_phone_number = '',
                new_birth_date = '',
                new_profile_picture_link = id_token['profile_picture'],
                session = session
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
            is_active = int(id_token['email_verified']),
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
            session
        )
        return set_current_user(new_user.user_id)

async def get_discovery_document(client: httpx.AsyncClient):
    async with client() as async_client:
        res = await async_client.get(GOOGLE_DISCOVERY_DOCUMENT_URL)
        return res.json()