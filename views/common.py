from fastapi import APIRouter
from fastapi_chameleon import template

router = APIRouter()

@router.get('/common/categories')
@template()
async def categories():
    return {}

@router.get('/common/pricing')
@template()
async def pricing():
    return {}