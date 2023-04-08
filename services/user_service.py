from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.user import UserAccount, UserLoginData, UserLoginDataExt

async def get_user_by_email(email: str, session: AsyncSession) -> UserLoginData | None:
    query = await session.execute(select(UserLoginData).where(UserLoginData.email_addr == email))
    user = query.scalar_one_or_none()
    
    return user

async def get_user_by_id(id: int, session: AsyncSession) -> UserLoginData:
    query = await session.execute(select(UserLoginData).where(UserLoginData.user_id == id))
    user = query.scalar_one_or_none()
    
    return user

async def get_user_account_by_id(id: int, session: AsyncSession) -> UserAccount:
    query = await session.execute(select(UserAccount).where(UserAccount.user_id == id))
    user = query.scalar_one_or_none()
    
    return user

async def set_email_confirmation_token(user_id: int, token: str, expiration_time: datetime, session: AsyncSession):
    user = await get_user_by_id(user_id, session)
    user.confirm_token = token
    user.confirm_token_time = expiration_time
    await session.commit()

async def set_user_recovery_token(user: UserLoginData, recovery_token_hash: str, recovery_token_time: datetime, session: AsyncSession):
    user = await get_user_by_id(user.user_id, session)
    user.recovery_token = recovery_token_hash
    user.recovery_token_time = recovery_token_time
    await session.commit()

async def get_user_by_recovery_token(token: str, session: AsyncSession)-> UserLoginData:
    result = await session.execute(select(UserLoginData).where(UserLoginData.recovery_token == token))
    user = result.scalar_one_or_none()

    return user

async def get_user_by_email_token(token: str, session: AsyncSession) -> UserLoginData:
    result = await session.execute(select(UserLoginData).where(UserLoginData.confirm_token == token))
    user = result.scalar_one_or_none()

    return user

async def get_user_by_google_hash(token: str, session: AsyncSession) -> UserLoginDataExt:
    result = await session.execute(select(UserLoginDataExt).where(UserLoginDataExt.external_provider_token == token))
    user_ext_data = result.scalar_one_or_none()
    return user_ext_data

async def update_user_email_validation_status(user: UserLoginData, session: AsyncSession):
    user.email_validation_status_id = 3
    user.user.is_active = 1
    await session.commit()

async def update_user_password(user: UserLoginData, new_hashed_password: str, new_password_salt: str, session: AsyncSession):
    user.password_hash = new_hashed_password
    user.password_salt = new_password_salt
    await session.commit()

async def create_user(username: str, phone_number: str, birth_date: str, is_active: int, session: AsyncSession, image_url: str | None = None) -> UserAccount:
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

async def create_user_ext(user: UserAccount, token: str, external_provider_id: int, session: AsyncSession):
    external_data = UserLoginDataExt(external_provider_token = token, external_provider_id = external_provider_id, user_id = user.user_id)
    session.add(external_data)
    await session.commit()
    await session.refresh(user)

async def create_user_login_data(user_id: int, hashed_password: str, password_salt: str, email: str, hash_algo_id: int, email_validation_status_id: int, session: AsyncSession) -> UserLoginData:
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