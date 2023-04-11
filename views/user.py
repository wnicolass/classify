from typing import Annotated
from fastapi import (
    APIRouter, 
    Depends,
    Request,
    responses,
    status
)
from fastapi_chameleon import template
from chameleon import PageTemplateFile
from common.viewmodel import ViewModel
from common.auth import requires_authentication
from common.auth import get_current_auth_user
from common.fastapi_utils import get_db_session, form_field_as_str
from sqlalchemy.ext.asyncio import AsyncSession
from services import user_service
from models.user import UserAccount
from common.utils import (
    is_valid_birth_date, 
    is_valid_username,
    is_valid_phone_number,
    handle_phone
)

router = APIRouter()

@router.get('/user/dashboard', dependencies = [Depends(requires_authentication)])
@template()
async def dashboard():
    return await ViewModel()

@router.get('/user/profile-settings', dependencies = [Depends(requires_authentication)])
@template('user/profile-settings.pt')
async def profile_settings():
    user = await get_current_auth_user()
    return await ViewModel(
        name = user.username,
        email = '',
        phone_number = user.phone_number,
        birth_date = user.birth_date
    )
    
@router.post('/user/profile-settings')
@template('user/profile-settings.pt')
async def profile_settings(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_db_session)]
):
    user = await get_current_auth_user()
    vm = await profile_settings_viewmodel(request, session, user)
    
    vm.name = user.username
    vm.email = ''
    vm.phone_number = user.phone_number
    vm.birth_date = user.birth_date
    
    if vm.error:
        return vm
    
    template = PageTemplateFile('./templates/user/profile-settings.pt')
    content = template(**vm)
    return responses.HTMLResponse(content, status_code = status.HTTP_200_OK)

async def profile_settings_viewmodel(
    request: Request, 
    session: Annotated[AsyncSession, Depends(get_db_session)],
    user: UserAccount
):
    form_data = await request.form()
    
    vm = await ViewModel(
        new_username = form_field_as_str(form_data, 'username'),
        new_phone_number = form_field_as_str(form_data, 'phone_number'),
        new_birth_date = form_field_as_str(form_data, 'birth_date')
    )
    
    if not is_valid_username(vm.new_username):
        vm.error, vm.error_msg = True, 'Username inválido!'
    elif not is_valid_phone_number(vm.new_phone_number):
        vm.error, vm.error_msg = True, 'Número de telemóvel inválido!'    
    elif not is_valid_birth_date(vm.new_birth_date):
        vm.error, vm.error_msg = True, 'Data de nascimento inválida!'
    if not vm.error:
        if user:
            await user_service.update_user_details(user, vm.new_username, handle_phone(vm.new_phone_number), vm.new_birth_date, session)
            vm.success, vm.success_msg = True, 'Dados da conta alterados com sucesso!.'
    
    return vm

@router.get('/user/my-ads', dependencies = [Depends(requires_authentication)])
@template('user/my-ads.pt')
async def my_ads():
    return await ViewModel()

@router.get('/user/offermessages', dependencies = [Depends(requires_authentication)])
@template()
async def offermessages():
    return await ViewModel()

@router.get('/user/payments', dependencies = [Depends(requires_authentication)])
@template()
async def payments():
    return await ViewModel()

@router.get('/user/favourite-ads', dependencies = [Depends(requires_authentication)])
@template('user/favourite-ads.pt')
async def favourite_ads():
    return await ViewModel()

@router.get('/user/privacy-setting', dependencies = [Depends(requires_authentication)])
@template('user/privacy-setting.pt')
async def privacy_setting():
    return await ViewModel()