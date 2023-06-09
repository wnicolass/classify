import os
from typing import Any
from dotenv import (
    load_dotenv, 
    find_dotenv
)
from hashlib import sha512
from fastapi import (
    HTTPException, 
    Request, 
    status
)
from passlib.context import CryptContext
from models.user import UserAccount
from middlewares.global_request import global_request
from services.user_service import get_user_account_by_id
from config.database import Session

load_dotenv(find_dotenv())

hash_context = CryptContext(schemes = ['bcrypt'], deprecated = 'auto')
SESSION_SECRET = os.getenv('COOKIE_SECRET')
RECOVERY_TOKEN_SECRET = os.getenv('RECOVERY_TOKEN_SECRET')

def check_password(password: str, hashed_password: str) -> bool:
    return hash_context.verify(password, hashed_password)

def hash_password(password: str) -> str:
    return hash_context.hash(password)

def hash_sub(sub: str, secret: str) -> str:
    return sha512(f'{sub}{secret}'.encode('utf-8')).hexdigest()

def hash_recovery_token(token: str) -> str:
    return sha512(f'{token}{RECOVERY_TOKEN_SECRET}'
    .encode('utf-8')).hexdigest()

class HTTPUnauthorizedAccess(HTTPException):
    def __init__(self, *args, **kwargs):
        super().__init__(
            status_code = status.HTTP_401_UNAUTHORIZED, 
            *args, 
            **kwargs
        )

class HTTPUnauthenticatedOnly(HTTPUnauthorizedAccess):
    pass

class InvalidToken(Exception):
    def __init__(self, user_id):
        self.user_id = user_id
class ExternalLoginError(HTTPException):
    def __init__(self, *args, **kargs):
        super().__init__(
            status_code = status.HTTP_401_UNAUTHORIZED, 
            *args, 
            **kargs
        )

async def requires_unauthentication():
    if await get_current_user():
        raise HTTPUnauthenticatedOnly(
            detail = 'This area requires unauthentication'
        )
    
async def requires_authentication():
    if not await get_current_user():
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER,
            headers={'Location': '/auth/sign-in'})
    
async def requires_authentication_secure():
    if not await get_current_user():
        raise HTTPUnauthorizedAccess(
            detail = 'This area requires authentication'
        )

"""
    The following lines of code were taken from:
    https://github.com/jfgalamba/Courseca22031
"""
def get_session(session_attr = 'session') -> Any:
    request = global_request.get()
    return getattr(request, session_attr)

async def get_current_user(
    request: Request | None = None
) -> UserAccount | None:
    if request is None:
        request  = global_request.get()
    user_id = request.session.get('user_id')
    if isinstance(user_id, int):
        async with Session() as session:
            user = await get_user_account_by_id(user_id, session)
            return user
    return None

def set_current_user(user_id: int):
    request = global_request.get()
    request.session['user_id'] = user_id

def remove_current_user():
    request = global_request.get()
    del request.session['user_id']
