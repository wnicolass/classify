import os
import secrets
from enum import Enum
from typing import List
from dotenv import (
    load_dotenv, 
    find_dotenv
)
from datetime import datetime, timedelta
from pytz import timezone
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import EmailStr
from chameleon import PageTemplateFile
from models.user import UserLoginData
from services.user_service import (
    set_email_confirmation_token,
    set_user_recovery_token
)
from common.auth import hash_recovery_token

load_dotenv(find_dotenv())

mail_config = ConnectionConfig(
    MAIL_USERNAME = os.getenv('EMAIL'),
    MAIL_PASSWORD= os.getenv('EMAIL_PASSWORD'),
    MAIL_FROM = os.getenv('EMAIL'),
    MAIL_PORT = 587,
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_STARTTLS = True,
    MAIL_SSL_TLS = False,
    USE_CREDENTIALS = True
)

async def send_email(
        email: List[EmailStr], 
        user: UserLoginData, 
        session: AsyncSession
):
    pt_tz = timezone('Portugal')
    expiration_time = datetime.now(tz = pt_tz) + timedelta(minutes = 60)
    payload = {
        'sub': str(user.user_id),
        'exp': expiration_time,
        'iat': datetime.now(tz = pt_tz)
    }

    token = create_email_token(payload)
    await set_email_confirmation_token(user.user_id, token, expiration_time, session)

    template = PageTemplateFile('./templates/auth/email.pt')
    content = template(
        token = token
    )

    message = MessageSchema(
        subject = 'Classify Verificação de Conta',
        recipients = email,
        body = content,
        subtype = 'html'
    )

    fm = FastMail(mail_config)
    await fm.send_message(message = message)

def create_email_token(payload: dict):
    return jwt.encode(
        payload, 
        os.getenv('EMAIL_TOKEN_SECRET'), 
        algorithm = os.getenv('EMAIL_TOKEN_ALGO')
    )

async def send_reset_password_email(
    email: List[EmailStr], 
    user: UserLoginData, 
    session: AsyncSession
):
    pt_tz = timezone('Portugal')
    recovery_token = secrets.token_urlsafe(64)
    recovery_token_time = datetime.now(tz = pt_tz) + timedelta(minutes = 1)

    await set_user_recovery_token(user, hash_recovery_token(recovery_token), recovery_token_time, session)

    template = PageTemplateFile('./templates/auth/email-password.pt')
    content = template(
        recovery_token = recovery_token
    )

    message = MessageSchema(
        subject = 'Classify Redefinição de Senha',
        recipients = email,
        body = content,
        subtype = 'html'
    )

    fm = FastMail(mail_config)
    await fm.send_message(message = message)

class EmailValidationStatus(Enum):
    NOT_CONFIRMED = 1
    EMAIL_SENT = 2
    CONFIRMED = 3