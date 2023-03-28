from fastapi import APIRouter
from fastapi_chameleon import template

router = APIRouter()

@router.get('/posts/blog')
@template()
async def blog():
    return {}

@router.get('/posts/blog-details')
@template('posts/blog-details.pt')
async def blog_details():
    return {}