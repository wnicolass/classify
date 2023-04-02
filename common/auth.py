import os
from typing import Optional
from dotenv import (
    load_dotenv, 
    find_dotenv
)
from hashlib import sha512
from fastapi import (
    HTTPException, 
    Request, 
    Response, 
    status
)
from passlib.context import CryptContext
from models.user import UserAccount, UserLoginData
from middlewares.global_request import global_request

load_dotenv(find_dotenv())

hash_context = CryptContext(schemes = ['bcrypt'], deprecated = 'auto')
SECRET = os.getenv('COOKIE_SECRET')
current_user: Optional[UserLoginData] = None

def check_password(password: str, hashed_password: str) -> bool:
    return hash_context.verify(password, hashed_password)

def hash_password(password: str) -> str:
    return hash_context.hash(password)

def set_auth_cookie(response: Response, user: UserLoginData):
    global current_user
    cookie_value = f'{str(user.user_id)}:{hash_cookie_value(str(user.user_id))}'

    current_user = user
    response.set_cookie(
        os.getenv('COOKIE_NAME'),
        cookie_value,
        secure = False,
        httponly = True,
        samesite = 'lax',
        max_age = os.getenv('COOKIE_MAX_AGE')
    )

def delete_auth_cookie(response: Response):
    response.delete_cookie(os.getenv('COOKIE_NAME'))

def hash_cookie_value(cookie_value: str) -> str:
    return sha512(f'{cookie_value}{SECRET}'.encode('utf-8')).hexdigest()

def get_auth_from_cookie(request: Request) -> int | None:
    if not (cookie_value:= request.cookies.get(os.getenv('COOKIE_NAME'))):
        return None
    
    cookie_parts = cookie_value.split(':')
    if len(cookie_parts) != 2:
        return None
    
    user_id, hash_value_from_cookie = cookie_parts
    hash_for_check = hash_cookie_value(user_id)
    if hash_for_check != hash_value_from_cookie:
        return None
    
    return int(user_id) if user_id.isdigit() else None

def get_current_auth_user() -> UserAccount | None:
    if user_id := get_auth_from_cookie(global_request.get()):
        return user_id if current_user is not None and current_user.user_id == user_id else None
    return None
#:

class HTTPUnauthorizedAccess(HTTPException):
    def __init__(self, *args, **kwargs):
        super().__init__(status_code = status.HTTP_401_UNAUTHORIZED, *args, **kwargs)

class HTTPUnauthenticatedOnly(HTTPUnauthorizedAccess):
    pass

class HTTPInvalidToken(HTTPException):
    def __init__(self, *args, **kwargs):
            super().__init__(status_code = status.HTTP_400_BAD_REQUEST, *args, **kwargs)

def requires_unauthentication():
    if get_current_auth_user():
        raise HTTPUnauthenticatedOnly(detail = 'This area requires unauthenticatiion')
    
def requires_authentication():
    if not get_current_auth_user():
        raise HTTPUnauthorizedAccess(detail = 'This area requires authenticatiion')