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

@router.get('/user/dashboard')
@template()
async def dashboard():
    vm = await ViewModel()

    if not vm.is_logged_in:
        response = responses.RedirectResponse(url = '/auth/sign-in', status_code = status.HTTP_302_FOUND)
        return response
    return vm

@router.get('/user/profile-settings')
@template('user/profile-settings.pt')
async def profile_settings():
    vm = await ViewModel()

    if not vm.is_logged_in:
        response = responses.RedirectResponse(url = '/auth/sign-in', status_code = status.HTTP_302_FOUND)
        return response
    return vm

@router.get('/user/my-ads')
@template('user/my-ads.pt')
async def my_ads():
    vm = await ViewModel()

    if not vm.is_logged_in:
        response = responses.RedirectResponse(url = '/auth/sign-in', status_code = status.HTTP_302_FOUND)
        return response
    return vm

@router.get('/user/offermessages')
@template()
async def offermessages():
    vm = await ViewModel()

    if not vm.is_logged_in:
        response = responses.RedirectResponse(url = '/auth/sign-in', status_code = status.HTTP_302_FOUND)
        return response
    return vm

@router.get('/user/payments')
@template()
async def payments():
    vm = await ViewModel()

    if not vm.is_logged_in:
        response = responses.RedirectResponse(url = '/auth/sign-in', status_code = status.HTTP_302_FOUND)
        return response
    return vm

@router.get('/user/favourite-ads')
@template('user/favourite-ads.pt')
async def favourite_ads():
    vm = await ViewModel()

    if not vm.is_logged_in:
        response = responses.RedirectResponse(url = '/auth/sign-in', status_code = status.HTTP_302_FOUND)
        return response
    return vm

@router.get('/user/privacy-setting')
@template('user/privacy-setting.pt')
async def privacy_setting():
    vm = await ViewModel()

    if not vm.is_logged_in:
        response = responses.RedirectResponse(url = '/auth/sign-in', status_code = status.HTTP_302_FOUND)
        return response
    return vm