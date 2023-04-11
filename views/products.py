from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_chameleon import template
from common.fastapi_utils import get_db_session
from common.viewmodel import ViewModel
from services import category_service, ad_service

router = APIRouter()

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

@router.get('/products/product-details')
@template('products/product-details.pt')
async def products_details():
    return await ViewModel()