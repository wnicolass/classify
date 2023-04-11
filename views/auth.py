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
    hash_google_id,
    check_password,
    hash_recovery_token,
    set_auth_cookie,
    delete_auth_cookie,
    requires_unauthentication,
    InvalidToken
)
from common.email import (send_email, EmailValidationStatus, send_reset_password_email)
from services import user_service

router = APIRouter()
load_dotenv(find_dotenv())

@router.get('/auth/sign-up', dependencies = [Depends(requires_unauthentication)])
@template('auth/sign-up.pt')
async def sign_up():
    return await sign_up_viewmodel()

async def sign_up_viewmodel():
    return await ViewModel(
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
    
    template = PageTemplateFile('./templates/auth/email-sent.pt')
    content = template(**vm)
    return responses.HTMLResponse(content, status_code = status.HTTP_200_OK)

async def post_sign_up_viewmodel(
    request: Request, 
    session: Annotated[AsyncSession, Depends(get_db_session)],
    bg_task: BackgroundTasks
):
    form_data = await request.form()
    vm = await ViewModel(
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
        vm.user = user

    return vm

@router.patch('/auth/sign-up/resend-email/{user_id}', status_code = status.HTTP_200_OK)
async def resend_verification_email(
    user_id: int,
    session: Annotated[AsyncSession, Depends(get_db_session)]
):
    user = await user_service.get_user_by_id(user_id, session)

    if not user:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = 'User not found.')
    
    await send_email([user.email_addr], user, session)
    return {'message': 'Email reenviado com sucesso.'}

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
        raise InvalidToken(user_id = user.user_id)
    
    email_sent = user.email_validation_status_id == EmailValidationStatus.EMAIL_SENT.value
    if not user.is_active and email_sent:
        await user_service.update_user_email_validation_status(user, session)

        template = PageTemplateFile('./templates/auth/email-verified.pt')
        vm = await ViewModel(
            user = user
        )
        content = template(**vm)
        return responses.HTMLResponse(content, status_code = status.HTTP_200_OK)

@router.get('/auth/sign-in', dependencies = [Depends(requires_unauthentication)])
@template('auth/sign-in.pt')
async def sign_in():
    return await sign_in_viewmodel()

async def sign_in_viewmodel():
    return await ViewModel(
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

    vm = await ViewModel(
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

    user.user.last_login = datetime.now()
    await session.commit()
    await session.refresh(user)
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

    hashed_id = hash_google_id(user_info['sub'])
    db_user = await user_service.get_user_by_google_hash(hashed_id, session)

    if not db_user:
        db_user = await user_service.create_user(
            username = user_info['name'], 
            phone_number = None, 
            birth_date = None, 
            image_url = user_info['picture'], 
            is_active = int(user_info['email_verified']), 
            session = session
        )
        await user_service.create_user_ext(db_user, hashed_id, 1, session)
    
    response = responses.RedirectResponse(url = '/', status_code = status.HTTP_302_FOUND)
    set_auth_cookie(response, db_user)
    db_user.user.last_login = datetime.now()
    await session.commit()
    return response

def google_sign_in_viewmodel(credentials: Credentials):
    id_info = verify_oauth2_token(credentials, requests.Request(), os.getenv('CLIENT_ID'), 1)
    
    if id_info['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
        raise ValueError('Invalid issuer')

    return id_info

@router.get('/auth/logout')
async def logout():
    response = responses.RedirectResponse(url = '/', status_code = status.HTTP_302_FOUND)
    delete_auth_cookie(response)
    return response

@router.get('/auth/reset-password', dependencies = [Depends(requires_unauthentication)])
@template(template_file = 'auth/email-reset-password.pt')
async def get_reset_password():
    return await get_reset_password_viewmodel()

async def get_reset_password_viewmodel():
    return await ViewModel()

@router.post('/auth/reset-password', dependencies = [Depends(requires_unauthentication)])
@template(template_file = 'auth/email-reset-password.pt')
async def reset_password(
    request: Request, 
    session: Annotated[AsyncSession, Depends(get_db_session)]
):
    vm = await reset_password_viewmodel(request, session)

    if vm.error:
        return vm

    return vm

async def reset_password_viewmodel(
    request: Request, 
    session: Annotated[AsyncSession, Depends(get_db_session)]
):
    form_data = await request.form()

    vm = await ViewModel(
        email = form_field_as_str(form_data, 'email')
    )

    if user:= await user_service.get_user_by_email(vm.email, session):
        await send_reset_password_email([vm.email], user, session)
        vm.success, vm.success_msg = True, 'E-mail enviado'
    else:
        vm.error, vm.error_msg = True, 'E-mail inválido.'

    return vm

@router.get('/auth/update-password', dependencies = [Depends(requires_unauthentication)])
@template(template_file = 'auth/update-password.pt')
async def get_update_password(token: str, session: Annotated[AsyncSession, Depends(get_db_session)]):
    return await get_update_password_viewmodel(token, session)

async def get_update_password_viewmodel(token: str, session: Annotated[AsyncSession, Depends(get_db_session)]):
    hashed_token = hash_recovery_token(token)

    if user:= await user_service.get_user_by_recovery_token(hashed_token, session):
        if datetime.now() > datetime.strptime(user.recovery_token_time, '%Y-%m-%d %H:%M:%S.%f'):
            template = PageTemplateFile('./templates/auth/email-reset-password.pt')
            vm = await ViewModel(
                error = True,
                error_msg = 'Token expirado, reinicie o processo.'
            )
            content = template(**vm)
            return responses.HTMLResponse(content, status_code = status.HTTP_200_OK)

    return await ViewModel(
        recovery_token = token
    )

@router.post('/auth/update-password', dependencies = [Depends(requires_unauthentication)])
@template(template_file = 'auth/update-password.pt')
async def update_password(
    request: Request,
    token: str,
    session: Annotated[AsyncSession, Depends(get_db_session)]
):
    vm = await update_password_viewmodel(request, token, session)
    
    if vm.error:
        vm.recovery_token = token
        return vm
    
    template = PageTemplateFile('./templates/auth/sign-in.pt')
    vm.email = ''
    vm.password = ''
    content = template(**vm)
    return responses.HTMLResponse(content, status_code = status.HTTP_200_OK)

async def update_password_viewmodel(
    request: Request,
    token: str,
    session: Annotated[AsyncSession, Depends(get_db_session)]
):
    form_data = await request.form()
    vm = await ViewModel(
        new_password = form_field_as_str(form_data, 'password'),
        confirm_new_password = form_field_as_str(form_data, 'confirm-password'),
    )

    hashed_token = hash_recovery_token(token)
    
    if not is_valid_password(vm.new_password) or not is_valid_password(vm.confirm_new_password):
        vm.error, vm.error_msg = True, 'Password inválida.'
    elif vm.new_password != vm.confirm_new_password:
        vm.error, vm.error_msg = True, 'Passwords não correspondem.'

    if not vm.error:
        if user:= await user_service.get_user_by_recovery_token(hashed_token, session):
            new_salt = uuid4().hex
            new_hashed_password = hash_password(vm.new_password + new_salt)
            await user_service.update_user_password(user, new_hashed_password, new_salt, session)
            vm.success, vm.success_msg = True, 'Senha alterada com sucesso. Faça login para comprar e vender.'
        
    return vm
