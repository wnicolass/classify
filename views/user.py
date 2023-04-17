import os
from typing import Annotated, List
from fastapi import (
    APIRouter, 
    Depends,
    UploadFile,
    Request,
    responses,
    status
)
from fastapi_chameleon import template
from chameleon import PageTemplateFile
from common.viewmodel import ViewModel
from common.auth import requires_authentication, requires_authentication_secure
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
from services import ad_service
from views.ad import fetch_countries
from config.cloudinary import upload_image

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
        phone_number = user.phone_number,
        birth_date = user.birth_date,
        all_countries = await fetch_countries()
    )
    
@router.post('/user/profile-settings', dependencies = [Depends(requires_authentication_secure)])
@template('user/profile-settings.pt')
async def profile_settings(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    file: UploadFile | None = None
):
    print(file)
    user = await get_current_auth_user()
    vm = await profile_settings_viewmodel(request, session, user, file)
    
    vm.name = user.username
    vm.phone_number = user.phone_number
    vm.birth_date = user.birth_date
    vm.all_countries = await fetch_countries()
    
    if vm.error:
        return vm
    
    template = PageTemplateFile('./templates/user/profile-settings.pt')
    content = template(**vm)
    return responses.HTMLResponse(content, status_code = status.HTTP_200_OK)

async def profile_settings_viewmodel(
    request: Request, 
    session: Annotated[AsyncSession, Depends(get_db_session)],
    user: UserAccount,
    file: UploadFile | None = None
):
    form_data = await request.form()
    
    vm = await ViewModel(
        new_username = form_field_as_str(form_data, 'username'),
        new_phone_number = form_field_as_str(form_data, 'phone_number'),
        new_birth_date = form_field_as_str(form_data, 'birth_date')
    )
    
    if vm.new_username != '' and not is_valid_username(vm.new_username):
        vm.error, vm.error_msg = True, 'Username inválido!'
    elif vm.new_phone_number != '' and not is_valid_phone_number(vm.new_phone_number):
        vm.error, vm.error_msg = True, 'Número de telemóvel inválido!'    
    elif vm.new_birth_date != '' and not is_valid_birth_date(vm.new_birth_date):
        vm.error, vm.error_msg = True, 'Data de nascimento inválida!'
        
    print(file)
    if file is not None:
        file_size_in_bytes = len(await file.read())
        file_size_in_kb = file_size_in_bytes / 1024
        file_ext = os.path.splitext(file.filename)[-1]
        if file_ext is not "":
            if file_size_in_kb > 500:
                vm.error, vm.error_msg = True, 'O tamanho limite da imagem é de 500kb.'
            elif file.content_type not in ('image/jpg', 'image/png', 'image/jpeg') or file_ext not in ['.jpg', '.jpeg', '.png']:
                vm.error, vm.error_msg = True, 'Apenas imagens do tipo ".png", ".jpg" ou ".jpeg".'
            await file.seek(0)
        
    if not vm.error:
        profile_picture_url = ''
        if file_ext is not "":
            url = upload_image(file)
            profile_picture_url = url['secure_url']
        if user:
            await user_service.update_user_details(
                user, 
                vm.new_username, 
                handle_phone(vm.new_phone_number), 
                vm.new_birth_date, 
                profile_picture_url,
                session)
            vm.success, vm.success_msg = True, 'Dados da conta alterados com sucesso!.'
    
    return vm

@router.get('/user/change-password', dependencies = [Depends(requires_authentication_secure)])
@template('user/change-password.pt')
async def dashboard():
    return await ViewModel()


@router.get('/user/my-ads', dependencies = [Depends(requires_authentication)])
@template('user/my-ads.pt')
async def my_ads(session: Annotated[AsyncSession, Depends(get_db_session)]):
    vm = await ViewModel()
    
    vm.ad_count_total = await ad_service.get_ad_count_by_user_id(session, vm.user_id)
    vm.ad_count_active = await ad_service.get_ad_count_by_user_id_and_status(session, vm.user_id, 1)
    vm.ad_count_inactive = await ad_service.get_ad_count_by_user_id_and_status(session, vm.user_id, 2)
    vm.ad_count_expired = await ad_service.get_ad_count_by_user_id_and_status(session, vm.user_id, 3)
    vm.ad_count_sold = await ad_service.get_ad_count_by_user_id_and_status(session, vm.user_id, 4)
    vm.ad_count_deleted = await ad_service.get_ad_count_by_user_id_and_status(session, vm.user_id, 5)
    vm.all_ads = await ad_service.get_ads_by_user_id(session, vm.user_id)
    vm.all_active_ads = await ad_service.get_ads_by_user_id_and_status(session, vm.user_id, 1)
    vm.all_inactive_ads = await ad_service.get_ads_by_user_id_and_status(session, vm.user_id, 2)
    vm.all_expired_ads = await ad_service.get_ads_by_user_id_and_status(session, vm.user_id, 3)
    vm.all_sold_ads = await ad_service.get_ads_by_user_id_and_status(session, vm.user_id, 4)
    vm.all_deleted_ads = await ad_service.get_ads_by_user_id_and_status(session, vm.user_id, 5)
    
    return vm

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

@router.post('/user/favourite/{ad_id}')
async def add_ad_to_favourites(
    ad_id: int, 
    session: Annotated[AsyncSession, Depends(get_db_session)]
):
    vm = await ViewModel()
    if not vm.user_id:
        return {'message': 'not logged in'}
    
    if ad_id in vm.user.fav_ads_id:
        return
    
    new_fav = await user_service.add_new_favourite(vm.user_id, ad_id, session)

    if new_fav:
        return {'msg': 'Ad added to favourites!'}
    
@router.delete('/user/favourite/{ad_id}', dependencies = [Depends(requires_authentication)])
async def delete_from_fav(
    ad_id: int,
    session: Annotated[AsyncSession, Depends(get_db_session)]
):
    vm = await ViewModel()
    for fav in vm.user.favourites:
        if fav.ad_id == ad_id and fav.user_id == vm.user_id:
            curr_user = await user_service.delete_user_favourite(vm.user, fav, session)
    
    return {'current_total_ads': len(curr_user.favourites)}

@router.get('/user/privacy-setting', dependencies = [Depends(requires_authentication)])
@template('user/privacy-setting.pt')
async def privacy_setting():
    return await ViewModel()