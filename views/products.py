from fastapi import APIRouter
from fastapi_chameleon import template
from common.viewmodel import ViewModel

router = APIRouter()

@router.get('/products/products')
@template()
async def products():
    return await ViewModel()

@router.get('/products/product-details')
@template('products/product-details.pt')
async def products_details():
    return await ViewModel()