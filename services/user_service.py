from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.user import UserAccount, UserLoginData

async def get_user_by_email(email: str, session: AsyncSession) -> UserLoginData | None:
    query = await session.execute(select(UserLoginData).where(UserLoginData.email_addr == email))
    user = query.scalar_one_or_none()
    
    return user

async def create_user(username: str, phone_number: str, birth_date: str, is_active: int, session: AsyncSession) -> UserAccount:
    user = UserAccount(
        username = username,
        phone_number = phone_number,
        birth_date = birth_date,
        is_active = is_active,
    )
    
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user

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