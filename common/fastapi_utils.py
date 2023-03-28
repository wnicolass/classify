from fastapi import UploadFile
from fastapi.datastructures import FormData
from sqlalchemy.ext.asyncio import AsyncSession
from config.database import Session

async def get_db_session():
    session: AsyncSession = Session()
    try:
        yield session
    finally:
        await session.close()

def form_field_as_str(form_data: FormData, field_name: str) -> str:
    field_value = form_data[field_name]
    if isinstance(field_value, str):
        return field_value
    raise TypeError(f'Form field {field_name} type is not str.')

def form_field_as_file(form_data: FormData, field_name: str) -> UploadFile:
    field_value = form_data[field_name]
    if isinstance(field_value, UploadFile):
        return field_value
    raise TypeError(f'Form field {field_name} type is UploadFile.')