from fastapi import APIRouter
from fastapi_chameleon import template

router = APIRouter()

@router.get('/products/product')
@template()
async def product():
    return {}

@router.get('/products/product-details')
@template('products/product-details.pt')
async def products_details():
    return {}