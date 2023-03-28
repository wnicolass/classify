from fastapi import APIRouter
from fastapi_chameleon import template

router = APIRouter()

@router.get('/auth/sign-in')
@template('auth/sign-in.pt')
async def sign_in():
    return {}

@router.get('/auth/sign-up')
@template('auth/sign-up.pt')
async def sign_up():
    return {}