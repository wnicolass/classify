from datetime import datetime
from typing import List
from sqlalchemy import and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from models.user import (
    UserAccount, 
    UserLoginData, 
    UserLoginDataExt, 
    UserAddress, 
    Favourite, 
    ExternalProvider, 
    OpenIdConnectTokens
)
from models.chat import Chatroom, Message

# CREATE
async def create_user(
    username: str, 
    phone_number: str, 
    birth_date: str, 
    is_active: int, 
    session: AsyncSession, 
    image_url: str | None = None
) -> UserAccount:
    user = UserAccount(
        username = username,
        phone_number = phone_number,
        birth_date = birth_date,
        profile_image_url = image_url,
        is_active = is_active,
    )
    
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user

async def create_user_ext(
    user: UserAccount, 
    token: str, 
    session: AsyncSession,
    external_provider_id: int = 1 
):
    external_data = UserLoginDataExt(
        external_provider_token = token, 
        external_provider_id = external_provider_id, 
        user_id = user.user_id
    )
    session.add(external_data)
    await session.commit()
    await session.refresh(user)

async def create_user_login_data(
    user_id: int, 
    email: str, 
    email_validation_status_id: int, 
    session: AsyncSession,
    hashed_password: str | None = None, 
    password_salt: str | None = None, 
    hash_algo_id: int = 2 
) -> UserLoginData:
    user_login_data = UserLoginData(
        user_id = user_id,
        password_hash = hashed_password,
        password_salt = password_salt,
        email_addr = email,
        hash_algo_id = hash_algo_id,
        email_validation_status_id = email_validation_status_id
    )
    session.add(user_login_data)
    await session.commit()
    await session.refresh(user_login_data)
    return user_login_data

async def add_new_favourite(
    user_id: int, 
    ad_id: int,
    session: AsyncSession
) -> Favourite:
    fav = Favourite(user_id = user_id, ad_id = ad_id)
    session.add(fav)
    await session.commit()
    await session.refresh(fav)
    
    return fav

async def create_user_address(
    new_country: str,
    new_city: str,
    user_id: int,
    session: AsyncSession):
    
    user_address = UserAddress(
        country = new_country,
        city = new_city,
        user_id = user_id
    )
    session.add(user_address)
    await session.commit()
    await session.refresh(user_address)
    return user_address

async def save_oauth_tokens(
    state: str, 
    nonce: str, 
    session: AsyncSession
) -> OpenIdConnectTokens:
    token_instance = OpenIdConnectTokens(state = state, nonce = nonce)
    session.add(token_instance)
    await session.commit()
    await session.refresh(token_instance)

    return token_instance

# READ
async def get_user_by_email(email: str, session: AsyncSession) -> UserAccount:
    query = await session.execute(
        select(UserAccount)
        .join(UserLoginData)
        .where(UserLoginData.email_addr == email)
    )
    user = query.scalar_one_or_none()

    return user

async def get_user_login_data_by_email(
    email: str, 
    session: AsyncSession
) -> UserLoginData:
    query = await session.execute(
        select(UserLoginData)
        .where(UserLoginData.email_addr == email)
    )
    user = query.scalar_one_or_none()

    return user

async def get_user_login_data_by_id(
    id: int, 
    session: AsyncSession
) -> UserLoginData:
    query = await session.execute(
        select(UserLoginData).
        where(UserLoginData.user_id == id)
    )
    user = query.scalar_one_or_none()
    
    return user

async def get_user_account_by_id(
    id: int, 
    session: AsyncSession
) -> UserAccount:
    query = await session.execute(select(UserAccount)
        .where(UserAccount.user_id == id)
        .options(joinedload(UserAccount.favourites))
    )
    user = query.unique().scalar_one_or_none()
    return user

async def get_all_verified_users(session: AsyncSession) -> List[UserAccount]:
    query = await session.execute(
        select(UserAccount)
        .where(UserAccount.is_active == 1)
    )
    verified_users = query.unique().scalars().all()

    return verified_users

async def get_user_favs(user_id: int, session: AsyncSession) -> List[int]:
    query = await session.execute(select(Favourite.ad_id)
        .where(Favourite.user_id == user_id)
    )
    user_favs_ids = query.unique().scalars().all()
    return user_favs_ids


async def get_user_by_recovery_token(
    token: str, 
    session: AsyncSession
)-> UserLoginData:
    result = await session.execute(
        select(UserLoginData)
        .where(UserLoginData.recovery_token == token)
    )
    user = result.scalar_one_or_none()

    return user

async def get_user_by_email_token(
    token: str, 
    session: AsyncSession
) -> UserLoginData:
    result = await session.execute(
        select(UserLoginData)
        .where(UserLoginData.confirm_token == token)
    )
    user = result.scalar_one_or_none()

    return user

async def get_user_by_hashed_sub(
    token: str, 
    session: AsyncSession, 
    ext_provider_id: int = 1
) -> UserAccount:
    result = await session.execute(
        select(UserAccount)
        .join(UserLoginDataExt)
        .join(ExternalProvider)
        .where(UserLoginDataExt.external_provider_token == token)
        .where(ExternalProvider.id == ext_provider_id)
    )
    user_ext_data = result.scalar_one_or_none()
    return user_ext_data
    
async def get_user_address_by_user_id(
    user_id: int, 
    session: AsyncSession
) -> UserAddress:
    result = await session.execute(
        select(UserAddress)
        .where(UserAddress.user_id == user_id)
    )
    user_address = result.scalar_one_or_none()
    return user_address

async def get_external_provider_by_id(
    session: AsyncSession, 
    ext_provider_id: int = 1
) -> ExternalProvider:
    query_result = await session.execute(
        select(ExternalProvider)
        .where(ExternalProvider.id == ext_provider_id)
    )
    external_provider = query_result.scalar_one_or_none()

    return external_provider

async def get_oauth_tokens(
    state_token: str, 
    session: AsyncSession
) -> OpenIdConnectTokens:
    query = await session.execute(
        select(OpenIdConnectTokens)
        .where(OpenIdConnectTokens.state == state_token)
    )
    token_instance = query.scalar_one_or_none()

    return token_instance

async def send_message(
    buyer_user_id: int,
    seller_user_id: int,
    adv_id: int,
    text_message: str,
    session: AsyncSession
):
    chatroom = await get_chatroom_by_seller_and_buyer_id(
        seller_user_id, 
        buyer_user_id, 
        session
    )
    if not chatroom:
        chatroom = Chatroom(
            ad_id = adv_id, 
            starter_id = buyer_user_id,
            is_unread_receiver = 1,
            is_unread_starter = 0
        )
        session.add(chatroom)
        await session.commit()
        await session.refresh(chatroom)
        
    if buyer_user_id == chatroom.starter_id:
        chatroom.is_unread_receiver = 1
        chatroom.is_unread_starter = 0
        await session.commit()
        await session.refresh(chatroom)
    else:
        chatroom.is_unread_receiver = 0
        chatroom.is_unread_starter = 1
        await session.commit()
        await session.refresh(chatroom)

    message = Message(
        text_message = text_message,
        chatroom_id = chatroom.id,
        sender_user_id = buyer_user_id,
        receiver_user_id = seller_user_id,
    )
    session.add(message)
    await session.commit()
    await session.refresh(message)
    return message

async def get_chatroom_by_seller_and_buyer_id(
    seller_user_id: int,
    buyer_user_id: int,
    session: AsyncSession
) -> Chatroom | None:
    query = await session.execute(
        select(Chatroom)
        .join(Chatroom.messages)
        .where(
            or_(and_(
                Message.sender_user_id == buyer_user_id,
                Message.receiver_user_id == seller_user_id,
            ),
            and_(
                Message.sender_user_id == seller_user_id,
                Message.receiver_user_id == buyer_user_id,
            )
        ))
        .limit(1)
    )
    chatroom = query.scalar_one_or_none()

    return chatroom

async def get_chatroom_by_id(
    chatroom_id: int,
    session: AsyncSession
):
    query = await session.execute(
        select(Chatroom)
        .where(Chatroom.id == chatroom_id)
    )
    chatroom = query.scalar_one_or_none() 

    return chatroom

async def get_senders_messages_by_current_user_id(
        current_user_id: int,
        session: AsyncSession
):
    messages_with_current_user = (
        select(Message.receiver_user_id)
        .where(
            or_(
                Message.receiver_user_id == current_user_id,
                Message.sender_user_id == current_user_id,
            )
        )
        .subquery()
    )

    users_ids = (
        select(UserAccount.user_id)
        .where(
            UserAccount.user_id.in_(messages_with_current_user)
        )
        .subquery()
    )

    users = await session.execute(
        select(UserAccount)
        .where(
            and_(
                UserAccount.user_id.in_(users_ids),
                UserAccount.user_id != current_user_id
            )
        )
    )
    chat_users = users.unique().scalars().all()
    print(chat_users)
    
    return chat_users

async def get_messages_by_chatroom_id(
    chatroom_id: int,
    session: AsyncSession
) -> List[Message]:
    query = await session.execute(
        select(Message)
        .join(Message.chatroom)
        .where(Chatroom.id == chatroom_id)
        .order_by(Message.send_at.asc()) # old = asc
    )
    messages = query.unique().scalars().all()

    return messages

# UPDATE
async def set_chatroom_as_read(
    chatroom_id: int,
    current_user_id: int,
    session: AsyncSession
):
    chatroom = await get_chatroom_by_id(chatroom_id, session)
    if chatroom.starter_id == current_user_id:
        chatroom.is_unread_starter = 0
    else:
        chatroom.is_unread_receiver = 0
    await session.commit()

async def set_email_confirmation_token(
    user_id: int, 
    token: str, 
    expiration_time: datetime, 
    session: AsyncSession
):
    user = await get_user_login_data_by_id(user_id, session)
    user.confirm_token = token
    user.confirm_token_time = expiration_time
    await session.commit()

async def set_user_recovery_token(
    user: UserLoginData, 
    recovery_token_hash: str, 
    recovery_token_time: datetime, 
    session: AsyncSession
):
    user = await get_user_login_data_by_id(user.user_id, session)
    user.recovery_token = recovery_token_hash
    user.recovery_token_time = recovery_token_time
    await session.commit()

async def update_user_details(
    user: UserAccount, 
    new_username: str, 
    new_phone_number: str, 
    new_birth_date: str,
    new_profile_picture_link: str,
    session: AsyncSession):

    db_user = await get_user_account_by_id(user.user_id, session)
    if new_username != '':
        db_user.username = new_username
    if new_phone_number != '':
        db_user.phone_number = new_phone_number
    if new_birth_date != '':
        db_user.birth_date = new_birth_date
    if new_profile_picture_link != '':
        db_user.profile_image_url = new_profile_picture_link
    
    await session.commit()
    await session.refresh(db_user)
    
async def update_user_address(
    user_address: UserAddress,
    new_country: str,
    new_city: str,
    session: AsyncSession):
    user_address.country = new_country
    user_address.city = new_city

    await session.commit()

async def update_user_email_validation_status(
    user: UserLoginData, 
    session: AsyncSession
):
    user.email_validation_status_id = 3
    user.user.is_active = 1
    await session.commit()

async def update_user_password(
    user: UserLoginData, 
    new_hashed_password: str, 
    new_password_salt: str, 
    session: AsyncSession
):
    user.password_hash = new_hashed_password
    user.password_salt = new_password_salt
    await session.commit()
    
# DELETE
async def delete_user_favourite(
    current_user: UserAccount, 
    fav: Favourite, 
    session: AsyncSession
) -> None:
    await session.delete(fav)
    await session.commit()
    current_user = await get_user_account_by_id(current_user.user_id, session)
    return current_user

async def delete_token_instance(
    token_instance: OpenIdConnectTokens, 
    session: AsyncSession
) -> None:
    await session.delete(token_instance)
    await session.commit()
