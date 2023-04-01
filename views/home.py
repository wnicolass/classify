from fastapi import APIRouter
from fastapi_chameleon import template
from common.viewmodel import ViewModel

router = APIRouter()

@router.get('/')
@template()
async def index():
    return ViewModel()

@router.get('/home/about')
@template()
async def about():
    return {}

@router.get('/home/contact')
@template()
async def contact():
    return {}

@router.get('/home/faq')
@template()
async def faq():
    return {}

@router.get('/home/post-ads')
@template('home/post-ads.pt')
async def post_ads():
    return {}