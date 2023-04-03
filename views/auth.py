import os
from dotenv import load_dotenv, find_dotenv
from typing import Annotated
from datetime import date, datetime
from fastapi import (APIRouter, Depends, HTTPException, Request, responses, status, BackgroundTasks)
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_chameleon import template
from chameleon import PageTemplateFile
from uuid import uuid4
from google.oauth2.credentials import Credentials
from google.oauth2.id_token import verify_oauth2_token
from google.auth.transport import requests
from common.viewmodel import ViewModel
from common.fastapi_utils import get_db_session, form_field_as_str
from common.utils import (
    is_valid_birth_date, 
    MIN_DATE, 
    is_valid_email, 
    is_valid_password,
    is_valid_username,
    is_valid_phone_number,
    handle_phone
)
from common.auth import (
    hash_password,
    check_password,
    set_auth_cookie,
    delete_auth_cookie,
    requires_unauthentication,
    HTTPInvalidToken
)
from common.email import (send_email, EmailValidationStatus)
from services import user_service

router = APIRouter()
load_dotenv(find_dotenv())

@router.get('/auth/sign-up', dependencies = [Depends(requires_unauthentication)])
@template('auth/sign-up.pt')
async def sign_up():
    return sign_up_viewmodel()

def sign_up_viewmodel():
    return ViewModel(
        min_date = MIN_DATE,
        max_date = date.today()
    )

@router.post('/auth/sign-up')
@template('auth/sign-up.pt')
async def sign_up(
    request: Request, 
    session: Annotated[AsyncSession, Depends(get_db_session)],
    bg_task: BackgroundTasks
):
    vm = await post_sign_up_viewmodel(request, session, bg_task)

    if vm.error:
        return vm
    
    response = responses.RedirectResponse(url = '/', status_code = status.HTTP_302_FOUND)
    return response

async def post_sign_up_viewmodel(
    request: Request, 
    session: Annotated[AsyncSession, Depends(get_db_session)],
    bg_task: BackgroundTasks
):
    form_data = await request.form()
    vm = ViewModel(
        username = form_field_as_str(form_data, 'username'),
        email = form_field_as_str(form_data, 'email'),
        birth_date = form_field_as_str(form_data, 'birth-date'),
        phone_number = form_field_as_str(form_data, 'phone-number'),
        password = form_field_as_str(form_data, 'password'),
        confirm_password = form_field_as_str(form_data, 'confirm-password'),
        min_date = MIN_DATE,
        max_date = date.today()
    )

    if not is_valid_username(vm.username):
        vm.error, vm.error_msg = True, 'Username inválido!'
    elif not is_valid_email(vm.email):
        vm.error, vm.error_msg = True, 'Email inválido!'
    elif not is_valid_password(vm.password) or not is_valid_password(vm.confirm_password):
        vm.error, vm.error_msg = True, 'Senha inválida!'
    elif not is_valid_birth_date(vm.birth_date):
        vm.error, vm.error_msg = True, 'Data inválida!'
    elif not is_valid_phone_number(vm.phone_number):
        vm.error, vm.error_msg = True, 'Número de telemóvel inválido!'
    elif await user_service.get_user_by_email(vm.email, session):
        vm.error, vm.error_msg = True, f'Endereço de email {vm.email} já existe'
    elif vm.password != vm.confirm_password:
        vm.error, vm.error_msg = True, 'Senhas não correspondem!'
    else:
        vm.error, vm.error_msg = False, ''

    if not vm.error:
        user = await user_service.create_user(
            vm.username,
            handle_phone(vm.phone_number),
            vm.birth_date,
            0, 
            session
        )

        salt = uuid4().hex
        hashed_password = hash_password(vm.password + salt)
        user_data = await user_service.create_user_login_data(
            user.user_id,
            hashed_password,
            salt,
            vm.email,
            2,
            2,
            session
        )
        bg_task.add_task(send_email, [vm.email], user, session)

    return vm

@router.get('/verification', dependencies = [Depends(requires_unauthentication)])
async def email_verification(
    token: str, 
    session: Annotated[AsyncSession, Depends(get_db_session)]
):
    user = await user_service.get_user_by_email_token(token, session)

    if not user:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = 'Not Found.')

    is_token_expired = datetime.now() > datetime.strptime(user.confirm_token_time, '%Y-%m-%d %H:%M:%S.%f')
    if user and is_token_expired:
        raise HTTPInvalidToken(detail = 'Invalid or expired token.')
    
    email_sent = user.email_validation_status_id == EmailValidationStatus.EMAIL_SENT.value
    if not user.is_active and email_sent:
        await user_service.update_user_email_validation_status(user, session)

        template = PageTemplateFile('./templates/auth/email-verified.pt')
        content = template(**ViewModel())
        return responses.HTMLResponse(content, status_code = status.HTTP_200_OK)

@router.get('/auth/sign-in', dependencies = [Depends(requires_unauthentication)])
@template('auth/sign-in.pt')
async def sign_in():
    return sign_in_viewmodel()

def sign_in_viewmodel():
    return ViewModel(
        email = '',
        password  = ''
    )

@router.post('/auth/sign-in')
@template('auth/sign-in.pt')
async def post_sign_in(
    request: Request, 
    session: Annotated[AsyncSession, Depends(get_db_session)]
):
    vm = await post_sign_in_viewmodel(request, session)

    if vm.error:
        return vm
    
    response = responses.RedirectResponse(url = '/', status_code = status.HTTP_302_FOUND)
    set_auth_cookie(response, vm.user)
    return response

async def post_sign_in_viewmodel(
    request: Request, 
    session: Annotated[AsyncSession, Depends(get_db_session)]
):
    form_data = await request.form()

    vm = ViewModel(
        email = form_field_as_str(form_data, 'email'),
        password = form_field_as_str(form_data, 'password')
    )

    user = await user_service.get_user_by_email(vm.email, session)

    if not user:
        vm.error, vm.error_msg = True, f'Utilizador com email {vm.email} não encontrado.'
    elif not check_password(vm.password + user.password_salt, user.password_hash):
        vm.error, vm.error_msg = True, f'Credenciais inválidas, tente novamente.'
    elif user.is_active != 1:
        vm.error, vm.error_msg = True, f'Sua conta ainda não foi ativada, verifique seu endereço de e-mail.'

    vm.user = user
    return vm

@router.post('/auth/google')
async def google_sign_in(
    request: Request, 
    session: Annotated[AsyncSession, Depends(get_db_session)]
):
    form_data = await request.form()
    credential = form_field_as_str(form_data, 'credential')
    user_info = google_sign_in_viewmodel(credential)

    user = await user_service.create_user(user_info['name'], None, None, 1, session)
    await user_service.create_user_ext(user_info['sub'], 1, user.user_id)
    
    return user_info

def google_sign_in_viewmodel(credentials: Credentials):
    id_info = verify_oauth2_token(credentials, requests.Request(), os.getenv('CLIENT_ID'))
    
    if id_info['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
        raise ValueError('Invalid issuer')

    return id_info

@router.get('/auth/logout')
async def logout():
    response = responses.RedirectResponse(url = '/', status_code = status.HTTP_302_FOUND)
    delete_auth_cookie(response)
    return response
