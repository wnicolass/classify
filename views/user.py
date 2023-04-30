import os
from typing import Annotated, List
from fastapi import (
    APIRouter, 
    Depends,
    UploadFile,
    Request,
    HTTPException,
    status
)
from fastapi_chameleon import template
from uuid import uuid4

from pydantic import BaseModel
from common.viewmodel import ViewModel
from common.auth import (
    requires_authentication,
    get_current_user,
    requires_authentication_secure,
    check_password,
    hash_password,
)
from common.fastapi_utils import get_db_session, form_field_as_str
from sqlalchemy.ext.asyncio import AsyncSession
from models.user import UserAccount, UserLoginData
from models.chat import Message as ChatMessage
from common.utils import (
    is_valid_birth_date, 
    is_valid_username,
    is_valid_password,
    is_valid_phone_number,
    handle_phone,
    add_plus_sign_to_phone_number,
    image_formats,
    transform_image_from_url
)
from services import (
    ad_service, 
    user_service,
    chat_service
)
from views.ad import fetch_countries
from config.cloudinary import upload_image

router = APIRouter()

@router.get(
    '/user/dashboard', 
    dependencies = [Depends(requires_authentication)]
)
@template()
async def dashboard():
    return await ViewModel()

@router.get(
    '/user/profile-settings', 
    dependencies = [Depends(requires_authentication)]
)
@template('user/profile-settings.pt')
async def profile_settings(
    session: Annotated[AsyncSession, Depends(get_db_session)]
):
    user = await get_current_user()
    address = await user_service.get_user_address_by_user_id(
        user.user_id, 
        session
    )
    
    vm: ViewModel = await ViewModel()
        
    vm.phone_number = add_plus_sign_to_phone_number(user.phone_number)
    vm.birth_date = user.birth_date
    if address:
        vm.country = address.country
        vm.city = address.city
    else:
        vm.country = ''
        vm.city = ''
    vm.all_countries = await fetch_countries()
        
    return vm
    
@router.post(
    '/user/profile-settings', 
    dependencies = [Depends(requires_authentication_secure)]
)
@template('user/profile-settings.pt')
async def profile_settings(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    file: UploadFile | None = None
):
    user = await get_current_user()
    vm = await profile_settings_viewmodel(request, session, user, file)
    address = await user_service.get_user_address_by_user_id(
        user.user_id, 
        session
    )
    
    vm.username = vm.new_username
    vm.phone_number = add_plus_sign_to_phone_number(vm.new_phone_number)
    vm.birth_date = vm.new_birth_date
    
    if address:
        vm.country = vm.new_country
        vm.city = vm.new_city
    else:
        vm.country = ''
        vm.city = ''
    vm.all_countries = await fetch_countries()
        
    if vm.new_profile_picture_url != "":
        vm.profile_image = transform_image_from_url(
            vm.new_profile_picture_url, 
            image_formats["square_fill"]
        )
    
    return vm

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
        new_birth_date = form_field_as_str(form_data, 'birth_date'),
        new_country = form_field_as_str(form_data, 'country'),
        new_city = form_field_as_str(form_data, 'city')
    )
    vm.new_profile_picture_url = ""
    
    if vm.new_username != '' and not is_valid_username(vm.new_username):
        vm.error, vm.error_msg = True, 'Username inválido!'
    elif vm.new_phone_number != '' and not is_valid_phone_number(
        vm.new_phone_number
    ):
        vm.error, vm.error_msg = True, 'Número de telemóvel inválido!'
    elif (
            vm.new_birth_date != '' and 
            not is_valid_birth_date(vm.new_birth_date)
        ):
        vm.error, vm.error_msg = True, 'Data de nascimento inválida!'
        
    if file is not None:
        file_size_in_bytes = len(await file.read())
        file_size_in_kb = file_size_in_bytes / 1024
        file_ext = os.path.splitext(file.filename)[-1]
        if file_ext != "":
            if file_size_in_kb > 500:
                vm.error, vm.error_msg = True, """
                    O tamanho limite da imagem é de 500kb.
                """
            elif (
                    file.content_type not in 
                    ('image/jpg', 'image/png', 'image/jpeg') or 
                    file_ext not in ['.jpg', '.jpeg', '.png']
                ):
                vm.error, vm.error_msg = True, """
                    Apenas imagens do tipo ".png", ".jpg" ou ".jpeg".
                """
            await file.seek(0)
    else:
        file_ext = ""         
            
    vm.all_countries = await fetch_countries()
    
    countries = []
    for country in vm.all_countries:
        countries.append(country['country'])
    
    if vm.new_country != '':
        if vm.new_country not in countries:
            vm.error, vm.error_msg = True, 'País inválido.'
        else:
            for dict in vm.all_countries:
                if dict['country'] == vm.new_country:
                    if vm.new_city not in dict['cities']:
                        vm.error, vm.error_msg = True, 'Cidade inválida.'

    if not vm.error:
        profile_picture_url = ''
        if file_ext != "":
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
        if user and vm.new_country != '' and vm.new_city != '':
            user_address = await user_service.get_user_address_by_user_id(
                vm.user_id, 
                session
            )
            if not user_address:
                user_address = await user_service.create_user_address(
                    vm.new_country,
                    vm.new_city,
                    vm.user_id,
                    session
                )
            else:
                await user_service.update_user_address(
                    user_address, 
                    vm.new_country, 
                    vm.new_city, 
                    session
                )
                
        if profile_picture_url:
            vm.new_profile_picture_url = profile_picture_url
        vm.success, vm.success_msg = True, """
            Dados da conta alterados com sucesso!
        """
    
    return vm

@router.get(
    '/user/change-password', 
    dependencies = [Depends(requires_authentication_secure)]
)
@template('user/change-password.pt')
async def change_password(
    session: Annotated[AsyncSession, Depends(get_db_session)]
):
    vm = await ViewModel()
    user_login_data = await user_service.get_user_login_data_by_id(
        vm.user.user_id, 
        session
    )
    
    if not user_login_data:
        raise HTTPException(status_code=404, detail="User data not found")
    
    password_hash = user_login_data.password_hash
        
    password_exists = True
    if not password_hash:    
        password_exists = False
        
    if vm.error:
        return vm
    
    return await change_password_viewmodel(session, password_exists)

async def change_password_viewmodel(password_exists: str):
    vm = await ViewModel()
    vm.password_exists = password_exists
    
    return vm

@router.post(
    '/user/change-password', 
    dependencies = [Depends(requires_authentication_secure)]
)
@template('user/change-password.pt')
async def submit_password(
    request: Request, 
    session: Annotated[AsyncSession, Depends(get_db_session)]
):
    vm = await ViewModel()
    user_login_data = await user_service.get_user_login_data_by_id(
        vm.user.user_id, 
        session
    )
    
    if not user_login_data:
        raise HTTPException(status_code=404, detail="User data not found")
    
    return await submit_password_viewmodel(request, session, user_login_data)

async def submit_password_viewmodel(
    request: Request, 
    session: Annotated[AsyncSession, Depends(get_db_session)],
    user_login_data: UserLoginData):
    
    password_hash = user_login_data.password_hash
    
    password_exists = True
    if not password_hash:    
        password_exists = False
        
    form_data = await request.form()
    
    vm = await ViewModel(
        current_password = form_field_as_str(
            form_data, 'current_password'
        ) if password_exists else '',
        new_password = form_field_as_str(form_data, 'new_password'),
        confirm_password = form_field_as_str(form_data, 'confirm_password'),
    )
    vm.password_exists = password_exists
    
    if password_exists:
        if not check_password(
            vm.current_password + user_login_data.password_salt,
            password_hash):
            vm.error, vm.error_msg = True, "A password atual está incorreta!"
        elif vm.new_password == vm.current_password:
            vm.error, vm.error_msg = True, "A password nova é igual á atual!"
    
    if vm.new_password != vm.confirm_password:
        vm.error, vm.error_msg = True, "A confirmação de password está incorreta"
    elif not is_valid_password(vm.new_password):
        vm.error, vm.error_msg = True, 'A nova password é inválida!'
        
    salt = uuid4().hex
    hashed_password = hash_password(vm.new_password + salt)
    
    if vm.error:
        return vm
    
    if hashed_password and salt:
        await user_service.update_user_password(
            user_login_data, 
            hashed_password, 
            salt, 
            session
        )
        vm.success, vm.success_msg = True, 'Password alterada com sucesso!'
    
    return vm

@router.get('/user/my-ads', dependencies = [Depends(requires_authentication)])
@template('user/my-ads.pt')
async def my_ads(session: Annotated[AsyncSession, Depends(get_db_session)]):
    vm = await ViewModel()
    
    vm.all_ads = await ad_service.get_ads_by_user_id(session, vm.user_id)
    vm.ad_count_total = len(vm.all_ads)
    
    vm.all_active_ads = ad_service.filter_ads_by_status(vm.all_ads, 1)
    vm.ad_count_active = len(vm.all_active_ads)
    
    vm.all_inactive_ads = ad_service.filter_ads_by_status(vm.all_ads, 2)
    vm.ad_count_inactive = len(vm.all_inactive_ads)
    
    vm.all_expired_ads = ad_service.filter_ads_by_status(vm.all_ads, 3)
    vm.ad_count_expired = len(vm.all_expired_ads)

    vm.all_sold_ads = ad_service.filter_ads_by_status(vm.all_ads, 4)
    vm.ad_count_sold = len(vm.all_sold_ads)
    
    vm.all_deleted_ads = ad_service.filter_ads_by_status(vm.all_ads, 5)
    vm.ad_count_deleted = len(vm.all_deleted_ads)

    vm.paid_promos = await ad_service.get_paid_promos(session)
    
    return vm

@router.get(
    '/user/offermessages', 
    dependencies = [Depends(requires_authentication)]
)
@template()
async def offermessages(
    session: Annotated[AsyncSession, Depends(get_db_session)]
):
    return await offermessages_viewmodel(session)

async def offermessages_viewmodel(
    session: Annotated[AsyncSession, Depends(get_db_session)]
):
    vm = await ViewModel()
    
    vm.senders = await chat_service.get_senders_messages_by_current_user_id(
        vm.user_id, 
        session
    )

    for sender in vm.senders:
        chatroom = await chat_service.get_chatroom_by_seller_and_buyer_id(
            vm.user_id, 
            sender.user_id, 
            session
        )
        if chatroom:
            setattr(sender, 'chatroom', chatroom)

    return vm

@router.patch(
    '/user/chatroom/{chatroom_id}', 
    dependencies = [Depends(requires_authentication)]
)
async def update_chatroom(
    chatroom_id: int, 
    session: Annotated[AsyncSession, Depends(get_db_session)]
):
    current_user = await get_current_user()
    await chat_service.set_chatroom_as_read(
        chatroom_id, 
        current_user.user_id, 
        session
    )

class ResponseChatroom(BaseModel):
    messages: List[ChatMessage]
    user_id: int

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True

class Message(BaseModel):
    text_message: str
    receiver_id: int

@router.get(
    '/user/offermessages/{chatroom_id}', 
    dependencies = [Depends(requires_authentication)]
)
async def chatroom_messages(
    chatroom_id: int,
    session: Annotated[AsyncSession, Depends(get_db_session)]
):
    """
        This endpoint is used to get all messages
        from a chatroom.
    """
    user = await get_current_user()
    
    response_chatroom =  ResponseChatroom(
        messages = await chat_service.get_messages_by_chatroom_id(
        chatroom_id, 
        session
    ),
        user_id = user.user_id
    )

    return response_chatroom
    
@router.post(
    '/user/chatroom/{chatroom_id}', 
    dependencies = [Depends(requires_authentication)]
)
async def send_ongoing_message(
    chatroom_id: int,
    message: Message,
    session: Annotated[AsyncSession, Depends(get_db_session)]
):
    chatroom = await chat_service.get_chatroom_by_id(chatroom_id, session)
    user = await get_current_user()

    message_info = await chat_service.send_message(
        user.user_id,
        message.receiver_id,
        chatroom.ad_id,
        message.text_message,
        session
    )
    return message_info

@router.get(
    '/user/payments', 
    dependencies = [Depends(requires_authentication)]
)
@template()
async def payments():
    return await ViewModel()

@router.get(
    '/user/favourite-ads', 
    dependencies = [Depends(requires_authentication)]
)
@template('user/favourite-ads.pt')
async def favourite_ads(
    session: Annotated[AsyncSession, Depends(get_db_session)]
):
    """
        As the user model has properties that holds
        information about all favourites, just need
        to return the view model to make this information
        available on the template
    """
    vm = await ViewModel()
    vm.fav_searches = await user_service.get_fav_searches_by_user_id(
        vm.user_id, 
        session
    )
    return vm

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
    
class SearchFavourite(BaseModel):
    url: str
    search_description: bool
    category: str
    subcategory: str
    order_type: str

@router.post('/user/favourite-search')
async def add_search_to_favourites(
    search_fav: SearchFavourite,
    session: Annotated[AsyncSession, Depends(get_db_session)]
):
    user = await get_current_user()
    if not user:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = 'User must be logged in'
        )
    
    all_user_fav_searches = await user_service.get_fav_searches_by_user_id(
        user.user_id, 
        session
    )
    
    for fav_search in all_user_fav_searches:
        if search_fav.url == fav_search.search_url:
            return {'success': False}
        
    new_favourite_search = await user_service.add_new_favourite_search(
        user.user_id, 
        search_fav.url.strip(), 
        search_fav.search_description,
        search_fav.category,
        search_fav.subcategory,
        search_fav.order_type,
        session
    )

    if new_favourite_search:
        return {'success': True}


@router.delete(
    '/user/favourite/{ad_id}', 
    dependencies = [Depends(requires_authentication)]
)
async def delete_from_fav(
    ad_id: int,
    session: Annotated[AsyncSession, Depends(get_db_session)]
):
    vm = await ViewModel()
    for fav in vm.user.favourites:
        if fav.ad_id == ad_id and fav.user_id == vm.user_id:
            curr_user = await user_service.delete_user_favourite(
                vm.user, 
                fav, 
                session
            )
    
    return {'current_total_ads': len(curr_user.favourites)}

@router.delete(
    '/user/favourite/search/{fav_search_id}', 
    dependencies = [Depends(requires_authentication)]
)
async def delete_fav_search(
    fav_search_id: int, 
    session: Annotated[AsyncSession, Depends(get_db_session)]
):
    if fav_search := await user_service.get_fav_search_by_id(
        fav_search_id, 
        session
    ):
        await user_service.delete_user_fav_search(fav_search, session)

@router.get(
    '/user/privacy-setting', 
    dependencies = [Depends(requires_authentication)]
)
@template('user/privacy-setting.pt')
async def privacy_setting():
    return await ViewModel()

@router.post(
    '/send_message/{adv_id}', 
    dependencies = [Depends(requires_authentication)]
)
async def send_message(
    adv_id: int,
    message: Message,
    session: Annotated[AsyncSession, Depends(get_db_session)]
):
    vm = await ViewModel()

    sender_user_id = vm.user_id

    if message_info := await user_service.send_message(
        sender_user_id,
        message.receiver_id,
        adv_id,
        message.text_message,
        session
    ):
        return {'success': True}
    
    return {'success': False}