import io
import os
import sys
import uuid
import aiofiles
import httpx
import pathlib
import cloudinary
from cloudinary.uploader import upload
from dotenv import load_dotenv, find_dotenv
from datetime import datetime
from decimal import Decimal as dec
from typing import Annotated, List
from fastapi import (
    APIRouter, 
    Depends,
    Request,
    UploadFile,
    responses,
    status
)
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_chameleon import template
from common.fastapi_utils import (
    form_field_as_str,
    form_field_as_file, 
    get_db_session
)
from common.viewmodel import ViewModel
from common.auth import requires_authentication
from services import category_service, ad_service
from common.utils import (
    is_valid_txt_field,
    is_valid_price,
    is_valid_phone_number
)
from services.user_service import get_user_account_by_id
from PIL import Image

load_dotenv(find_dotenv())
router = APIRouter()

cloudinary.config(
  cloud_name = os.getenv('CLOUDINARY_NAME'),
  api_key = os.getenv('CLOUDINARY_API_KEY'),
  api_secret = os.getenv('CLOUDINARY_SECRET'),
  secure = True
)

@router.get('/home/post-ads', dependencies = [Depends(requires_authentication)])
@template('home/post-ads.pt')
async def post_ads(session: Annotated[AsyncSession, Depends(get_db_session)]):
    return await post_ads_viewmodel(session)

async def post_ads_viewmodel(session: Annotated[AsyncSession, Depends(get_db_session)]):
    all_countries = await fetch_countries()
    features = await ad_service.get_all_features(session)
    conditions = await ad_service.get_all_ad_conditions(session)
    return await ViewModel(
        all_categories = await category_service.get_all_categories(session),
        all_countries = all_countries,
        all_features = features,
        all_ad_conditions = conditions
    )

async def fetch_countries():
    async with httpx.AsyncClient() as client:
        response = await client.get('https://countriesnow.space/api/v0.1/countries')
        json_res = response.json()
        all_countries = [country for country in json_res['data']]
        return all_countries

@router.post('/home/post-ads', dependencies = [Depends(requires_authentication)])
@template(template_file = 'home/post-ads.pt')
async def post_ad(request: Request, files: List[UploadFile], session: Annotated[AsyncSession, Depends(get_db_session)]):
    vm = await post_ad_viewmodel(request, files, session)

    if vm.error:
        vm.all_categories = await category_service.get_all_categories(session)
        vm.all_countries = await fetch_countries()
        vm.all_features = await ad_service.get_all_features(session)
        vm.all_ad_conditions = await ad_service.get_all_ad_conditions(session)
        return vm
    
    return responses.RedirectResponse(url = '/user/my-ads', status_code = status.HTTP_302_FOUND)

async def post_ad_viewmodel(request: Request, files: list[UploadFile], session: Annotated[AsyncSession, Depends(get_db_session)]):
    form_data = await request.form()
    form_dict = form_data._dict
    vm = await ViewModel(
        title = form_field_as_str(form_dict, 'title'),
        category = form_field_as_str(form_dict, 'category'),
        subcategory = form_field_as_str(form_dict, 'subcategory'),
        brand = form_field_as_str(form_dict, 'brand'),
        authenticity = form_field_as_str(form_dict, 'authenticity'),
        condition = form_field_as_str(form_dict, 'condition'),
        price = form_field_as_str(form_dict, 'price'),
        is_negotiable = form_field_as_str(form_dict, 'negotiable') if 'negotiable' in form_dict else None,
        description = form_field_as_str(form_dict, 'description'),
        phone = form_field_as_str(form_dict, 'phone'),
        country = form_field_as_str(form_dict, 'country'),
        city = form_field_as_str(form_dict, 'city')
    )

    if not is_valid_txt_field(vm.title):
        vm.error, vm.error_msg = True, 'Título inválido. Por favor, evite utilizar símbolos mais de três vezes seguidas.'
    elif vm.category == 'none':
        vm.error, vm.error_msg = True, 'Selecione uma categoria válida.'
    elif vm.subcategory == 'none':
        vm.error, vm.error_msg = True, 'Selecione uma subcategoria válida.'
    elif vm.authenticity == 'none':
        vm.error, vm.error_msg = True, 'Informe a autenticidade do produto.'
    elif vm.condition == 'none':
        vm.error, vm.error_msg = True, 'Selecione uma condição válida.'
    elif vm.country == 'none':
        vm.error, vm.error_msg = True, 'Selecione um país válido.'
    elif vm.city == 'none':
        vm.error, vm.error_msg = True, 'Selecione uma cidade válida.'
    elif not is_valid_txt_field(vm.brand):
        vm.error, vm.error_msg = True, 'Marca inválida. Por favor, evite utilizar símbolos mais de três vezes seguidas.'
    elif not is_valid_price(vm.price):
        vm.error, vm.error_msg = True, 'O preço deve estar no formato: 123456,50'
    elif len(vm.phone) > 0 and not is_valid_phone_number(vm.phone):
        vm.error, vm.error_msg = True, 'Insira um número de telemóvel com o seguinte formato: +351 123 456 789 ou 123 456 789'
    elif len(vm.description) > 1000 or not is_valid_txt_field(vm.description):
        vm.error, vm.error_msg = True, 'Descrição inválida. Por favor, evite utilizar símbolos mais de três vezes seguidas.'
    elif not len(files) >= 2:
        vm.error, vm.error_msg = True, 'O anúncio deve ter pelo menos duas 2 imagens.'
    elif len(files) >= 2:
        for file in files:
            file_size_in_bytes = len(await file.read())
            file_size_in_kb = file_size_in_bytes / 1024
            file_ext = os.path.splitext(file.filename)[-1]
            if file_size_in_kb > 500:
                vm.error, vm.error_msg = True, 'O tamanho limite das imagens é de 500kb.'
                break
            elif file.content_type not in ('image/jpg', 'image/png', 'image/jpeg') or file_ext not in ['.jpg', '.jpeg', '.png']:
                vm.error, vm.error_msg = True, 'Apenas imagens do tipo ".png", ".jpg" ou ".jpeg".'
                break
            await file.seek(0)
    elif user:= await get_user_account_by_id(vm.user_id, session):
        if not user.phone_number and len(vm.phone) == 0:
            vm.error, vm.error_msg = True, 'Insira um número de telemóvel com o seguinte formato: +351 123 456 789 ou 123 456 789'


    if not vm.error:
        path = pathlib.Path().cwd()
        uploads_dir = path / 'uploads'
        if not uploads_dir.exists():
            uploads_dir.mkdir()
        vm.files = []
        for file in files:
            url = upload(file.file, )
            vm.files.append({
                'filename': url['public_id'],
                'file_path': url['secure_url']
            })
        await ad_service.insert_ad(
            vm.title, 
            int(vm.subcategory), 
            vm.brand,
            int(vm.condition),
            dec(vm.price.replace(',', '.')),
            bool(vm.is_negotiable),
            vm.description,
            vm.files,
            vm.user_id,
            vm.country,
            vm.city,
            ad_status_id = 2,
            authenticity = 'Não original' if vm.authenticity == '0' else 'Original',
            session = session
        )

    return vm

@router.get('/home/ad/{category_id}')
async def get_subcategories(
    category_id: int,
    session: Annotated[AsyncSession, Depends(get_db_session)]
):
    subcategories = await category_service.get_subcategory_by_category_id(category_id, session)

    return subcategories
