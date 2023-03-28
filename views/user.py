from fastapi import APIRouter
from fastapi_chameleon import template

router = APIRouter()

@router.get('/user/dashboard')
@template()
async def dashboard():
    return {}

@router.get('/user/profile-settings')
@template('user/profile-settings.pt')
async def profile_settings():
    return {}

@router.get('/user/my-ads')
@template('user/my-ads.pt')
async def my_ads():
    return {}

@router.get('/user/offermessages')
@template()
async def offermessages():
    return {}

@router.get('/user/payments')
@template()
async def payments():
    return {}

@router.get('/user/favourite-ads')
@template('user/favourite-ads.pt')
async def favourite_ads():
    return {}

@router.get('/user/privacy-setting')
@template('user/privacy-setting.pt')
async def privacy_setting():
    return {}