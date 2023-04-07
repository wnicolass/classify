from typing import Annotated
from fastapi import (
    APIRouter, 
    Depends
)
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_chameleon import template
from common.fastapi_utils import get_db_session
from common.viewmodel import ViewModel
from common.auth import requires_authentication
from services import category_service

router = APIRouter()

@router.get('/home/post-ads', dependencies = [Depends(requires_authentication)])
@template('home/post-ads.pt')
async def post_ads(session: Annotated[AsyncSession, Depends(get_db_session)]):
    return await ViewModel(
        all_categories = await category_service.get_all_categories(session)
    )

@router.get('/home/ad/{category_id}')
async def get_subcategories(
    category_id: int,
    session: Annotated[AsyncSession, Depends(get_db_session)]
):
    subcategories = await category_service.get_subcategory_by_category_id(category_id, session)

    return subcategories
