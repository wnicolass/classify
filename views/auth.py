from typing import Annotated
from datetime import date, datetime
from fastapi import (APIRouter, Depends, Request, responses, status, BackgroundTasks)
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_chameleon import template
from chameleon import PageTemplateFile
from uuid import uuid4
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
    check_password
)
from common.email import send_email
from services import user_service

router = APIRouter()

@router.get('/auth/sign-up')
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

@router.get('/verification')
async def email_verification(
    request: Request, 
    token: str, 
    session: Annotated[AsyncSession, Depends(get_db_session)]
):
    user = await user_service.get_user_by_email_token(token, session)

    if user:
        if not datetime.now() < datetime.strptime(user.confirm_token_time, '%Y-%m-%d %H:%M:%S.%f'):
            template = PageTemplateFile('./templates/errors/invalid-token.pt')
            content = template(**ViewModel())
            return responses.HTMLResponse(content, status_code = status.HTTP_200_OK)
        elif user.is_active != 1:
            user.user.is_active = 1
            await session.commit()

            template = PageTemplateFile('./templates/auth/email-verified.pt')
            content = template(**ViewModel())
            return responses.HTMLResponse(content, status_code = status.HTTP_200_OK)
    


@router.get('/auth/sign-in')
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

    return vm

