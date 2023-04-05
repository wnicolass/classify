from typing import Annotated
from fastapi import APIRouter, Depends
from fastapi_chameleon import template
from sqlalchemy.ext.asyncio import AsyncSession
from common.fastapi_utils import get_db_session
from common.viewmodel import ViewModel
from services import category_service

router = APIRouter()

@router.get('/common/categories')
@template()
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


@router.get('/common/pricing')
@template()
async def pricing():
    return await ViewModel()