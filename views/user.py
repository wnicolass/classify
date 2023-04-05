from fastapi import (
    APIRouter, 
    Depends,
    responses,
    status
)
from fastapi_chameleon import template
from common.viewmodel import ViewModel
from common.auth import requires_authentication

router = APIRouter()

@router.get('/user/dashboard', dependencies = [Depends(requires_authentication)])
@template()
async def dashboard():
    return await ViewModel()

@router.get('/user/profile-settings', dependencies = [Depends(requires_authentication)])
@template('user/profile-settings.pt')
async def profile_settings():
    return await ViewModel()

@router.get('/user/my-ads', dependencies = [Depends(requires_authentication)])
@template('user/my-ads.pt')
async def my_ads():
    return await ViewModel()

@router.get('/user/offermessages', dependencies = [Depends(requires_authentication)])
@template()
async def offermessages():
    return await ViewModel()

@router.get('/user/payments', dependencies = [Depends(requires_authentication)])
@template()
async def payments():
    return await ViewModel()

@router.get('/user/favourite-ads')
@template('user/favourite-ads.pt')
async def favourite_ads():
    vm = await ViewModel()

    if not vm.is_logged_in:
        response = responses.RedirectResponse(url = '/auth/sign-in', status_code = status.HTTP_302_FOUND)
        return response
    return vm

@router.get('/user/privacy-setting', dependencies = [Depends(requires_authentication)])
@template('user/privacy-setting.pt')
async def privacy_setting():
    return await ViewModel()