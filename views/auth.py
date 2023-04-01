from typing import Annotated
from datetime import date
from fastapi import APIRouter, Depends, Request, responses, status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_chameleon import template
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
from common.auth import hash_password
from services import user_service

router = APIRouter()

@router.get('/auth/sign-in')
@template('auth/sign-in.pt')
async def sign_in():
    return {}

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
    session: Annotated[AsyncSession, Depends(get_db_session)]
):
    vm = await post_sign_up_viewmodel(request, session)

    if vm.error:
        return vm
    
    response = responses.RedirectResponse(url = '/', status_code = status.HTTP_302_FOUND)
    return response

async def post_sign_up_viewmodel(
    request: Request, 
    session: Annotated[AsyncSession, Depends(get_db_session)]
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
    
    return vm