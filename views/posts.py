from fastapi import APIRouter
from fastapi_chameleon import template

from common.viewmodel import ViewModel

router = APIRouter()

@router.get('/posts/blog')
@template()
async def blog():
    return ViewModel()

@router.get('/posts/blog-details')
@template('posts/blog-details.pt')
async def blog_details():
    return ViewModel()