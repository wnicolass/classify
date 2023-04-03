from fastapi import (
    APIRouter, 
    Depends
)
from fastapi_chameleon import template
from common.viewmodel import ViewModel
from common.auth import requires_authentication

router = APIRouter()

@router.get('/')
@template()
async def index():
    return ViewModel()

@router.get('/home/about')
@template()
async def about():
    return ViewModel()

@router.get('/home/contact')
@template()
async def contact():
    return ViewModel()

@router.get('/home/faq')
@template()
async def faq():
    return ViewModel()

@router.get('/home/post-ads', dependencies = [Depends(requires_authentication)])
@template('home/post-ads.pt')
async def post_ads():
    return ViewModel()