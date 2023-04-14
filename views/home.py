from typing import Annotated
from fastapi import (
    APIRouter, 
    Depends
)
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_chameleon import template
from common.fastapi_utils import get_db_session
from common.viewmodel import ViewModel
from services import category_service, ad_service, user_service

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
        all_categories = await category_service.get_all_categories(session),
        popular_ads = await ad_service.get_popular_ads(session),
        recent_ads = await ad_service.get_ads_by_creation_date(session),
        total_ads = len(await ad_service.get_all_ads(session)),
        total_verified_users = len(await user_service.get_all_verified_users(session)),
        sold_ads = len(await ad_service.get_ads_by_status(session, 'vendido')),
        top_locations = await ad_service.get_locations_by_total_ads(session)
    )

@router.get('/about')
@template()
async def about():
    return await ViewModel()

@router.get('/contact')
@template()
async def contact():
    return await ViewModel()

@router.get('/faq')
@template()
async def faq():
    return await ViewModel()