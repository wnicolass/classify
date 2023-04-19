import os
from starlette.middleware.sessions import SessionMiddleware
from fastapi import FastAPI
from dotenv import (load_dotenv, find_dotenv)

load_dotenv(find_dotenv())

def add_session_middleware(app: FastAPI):
    app.add_middleware(
        SessionMiddleware, 
        session_cookie = os.getenv('COOKIE_NAME'),
        secret_key = os.getenv('COOKIE_SECRET'),
        same_site = 'lax',
        https_only = False,
        max_age = int(os.getenv('COOKIE_MAX_AGE'))
    )