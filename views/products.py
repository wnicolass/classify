from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_chameleon import template
from common.fastapi_utils import get_db_session
from common.viewmodel import ViewModel
from services import category_service, ad_service

router = APIRouter()

@router.get('/products/category/{category_id}')
@template(template_file='products/products.pt')
async def show_ads_category(category_id: int, session: Annotated[AsyncSession, Depends(get_db_session)]):
    return await ViewModel(
        all_categories = await category_service.get_all_categories(session),
        all_ads = await ad_service.get_ads_by_category_id(session, category_id)
    )

@router.get('/products/subcategory/{category_id}')
@template(template_file='products/products.pt')
async def show_ads_category(category_id: int, session: Annotated[AsyncSession, Depends(get_db_session)]):
    return await ViewModel(
        all_categories = await category_service.get_all_categories(session),
        all_ads = await ad_service.get_ads_by_subcategory_id(session, category_id)
    )

@router.get('/products')
@template()
async def products(session: Annotated[AsyncSession, Depends(get_db_session)]):
    vm = await products_viewmodel(session)

    return vm

async def products_viewmodel(session: Annotated[AsyncSession, Depends(get_db_session)]):
    return await ViewModel(
       all_categories = await category_service.get_all_categories(session),
       all_ads = await ad_service.get_all_ads(session)
    )

@router.get('/products/ad/{ad_id}')
@template(template_file='products/product-details.pt')
async def show_ad(ad_id, session: Annotated[AsyncSession, Depends(get_db_session)]):
    return await ViewModel(
        get_3_ads = await ad_service.get_3_ads(session),
        adv = await ad_service.get_ad_by_id(session, ad_id)
    )

@router.get('/products/product-details')
@template('products/product-details.pt')
async def products_details():
    return await ViewModel()