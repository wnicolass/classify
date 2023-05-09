from typing import Annotated
from fastapi import APIRouter, Depends
from fastapi_chameleon import template
from sqlalchemy.ext.asyncio import AsyncSession
from common.fastapi_utils import get_db_session
from common.viewmodel import ViewModel
from services import category_service

router = APIRouter()

@router.get('/ad/categories/{category_id}')
async def get_subcategories(
    category_id: int,
    session: Annotated[AsyncSession, Depends(get_db_session)]
):
    subcategories = await category_service.get_subcategory_by_category_id(
        category_id, 
        session
    )

    return subcategories

@router.get('/categories')
@template(template_file= 'common/categories.pt')
async def categories(
    session: Annotated[AsyncSession, Depends(get_db_session)]
):
    vm = await categories_viewmodel(session)
    return vm

async def categories_viewmodel(
        session: Annotated[AsyncSession, Depends(get_db_session)]
):
    vm = await ViewModel()
    vm.all_categories = await category_service.get_all_categories(session)
    return vm

@router.get('/categories/{category_id}')
async def category_by_id(
    category_id: int,
    session: Annotated[AsyncSession, Depends(get_db_session)]
):
    return await category_service.get_category_by_id(
        category_id,
        session
    )

@router.get('/subcategories/{subcategory_id}')
async def category_by_id(
    subcategory_id: int,
    session: Annotated[AsyncSession, Depends(get_db_session)]
):
    return await category_service.get_subcategory_by_id(
        subcategory_id,
        session
    )

@router.get('/pricing')
@template(template_file= 'common/pricing.pt')
async def pricing():
    return await ViewModel()


@router.get('/privacy-policy')
@template('common/privacy-policy.pt')
async def privacy_policy():
    return await ViewModel()