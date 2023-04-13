from typing import Annotated
from fastapi import (
    APIRouter, 
    Depends
)
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_chameleon import template
from common.fastapi_utils import get_db_session
from common.viewmodel import ViewModel
from services import category_service, ad_service

router = APIRouter()

@router.get('/')
@template()
async def index(
    session: Annotated[AsyncSession, Depends(get_db_session)]
):
    vm = await index_viewmodel(session)
    return vm

async def index_viewmodel(
        session: Annotated[AsyncSession, Depends(get_db_session)]
):
    return await ViewModel(
        popular_categories = await category_service.popular_categories(session),
        all_cities = await ad_service.get_cities_with_ads(session),
        all_categories = await category_service.get_all_categories(session)
    )

@router.get('/home/about')
@template()
async def about():
    return await ViewModel()

@router.get('/home/contact')
@template()
async def contact():
    return await ViewModel()

@router.get('/home/faq')
@template()
async def faq():
    return await ViewModel()