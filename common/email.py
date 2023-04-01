import os
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
from services.user_service import set_email_confirmation_token

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
        subject = 'Classify Account Verification',
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

