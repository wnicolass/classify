import os
from starlette.middleware.sessions import SessionMiddleware
from fastapi import FastAPI
from dotenv import (load_dotenv, find_dotenv)

load_dotenv(find_dotenv())

"""
    In a starter version of this app we were using cookies
    to store user information on the browser, but we were only
    storing the user_id. As now we need to store more information
    (e.g. the nounce for oauth2 authentication) we are using sessions.
    A Session is just a way to store temporary user data on the server,
    through a unique session id that is stored on the browser.
    But have in mind that we are not storing that user temporary data
    on our server, we're storing in the cookies.
"""
def add_session_middleware(app: FastAPI):
    app.add_middleware(
        SessionMiddleware, 
        session_cookie = os.getenv('COOKIE_NAME'),
        secret_key = os.getenv('COOKIE_SECRET'),
        same_site = 'lax',
        https_only = False,
        max_age = int(os.getenv('COOKIE_MAX_AGE'))
    )