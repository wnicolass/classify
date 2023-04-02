from fastapi import APIRouter
from fastapi_chameleon import template
from common.viewmodel import ViewModel

router = APIRouter()

@router.get('/common/categories')
@template()
async def categories():
    return ViewModel()

@router.get('/common/pricing')
@template()
async def pricing():
    return ViewModel()