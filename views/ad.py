import os
import httpx
from decimal import Decimal as dec
from typing import Annotated, List
from fastapi import (
    APIRouter, 
    Depends,
    HTTPException,
    Request,
    UploadFile,
    responses,
    status
)
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_chameleon import template
from common.fastapi_utils import (
    form_field_as_str,
    get_db_session
)
from common.viewmodel import ViewModel
from common.auth import requires_authentication
from services import category_service, ad_service
from common.utils import (
    is_valid_txt_field,
    is_valid_price,
    is_valid_phone_number,
    get_min_max_price
)
from services.user_service import get_user_account_by_id
from config.cloudinary import upload_image

router = APIRouter()

@router.get('/ads/sort')
async def sort_ads_category(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    title: str | None = '',
    description: str | None = None,
    city: str | None = '',
    category_id: int | None = '',
    subcategory_id: int | None = '',
    order_by: str | None = '',
    min_price: dec = 0,
    max_price: dec = 0
):

    if subcategory_id and not category_id:
        category_id = await category_service.get_category_by_subcategory_id(subcategory_id, session)
    filtered_ads = await ad_service.get_ads_by_criteria(session, title, description, 
                city, category_id, subcategory_id, order_by,  min_price, max_price)

    vm = await ViewModel()
    
    response = {
        'ads': filtered_ads,
        'city': city,
        'order_by': order_by,
        'is_logged_in': vm.is_logged_in,
    }
    return response

@router.get('/ad/{ad_id}')
@template(template_file='products/product-details.pt')
async def show_ad(ad_id, session: Annotated[AsyncSession, Depends(get_db_session)]):
    current_ad = await ad_service.get_ad_by_id(session, ad_id)

    if not current_ad:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = {'error_msg': 'Not found'})

    return await ViewModel(
        adv = current_ad,
        get_3_ads = await ad_service.get_3_ads(current_ad, session)
    )

@router.get('/ads/category/{category_id}')
@template(template_file='products/products.pt')
async def show_ads_category(session: Annotated[AsyncSession, Depends(get_db_session)], category_id: str):

    all_ads = await ad_service.get_ads_by_asc(category_id, session)
    min, max = get_min_max_price(all_ads)

    return await ViewModel(
        all_categories = await category_service.get_all_categories(session),
        all_ads = all_ads,
        all_cities = await ad_service.get_cities_by_category(category_id, session),
        all_subcategories = await category_service.get_subcategory_by_category_id(category_id, session),
        in_subcategories_view = False,
        in_categories_view = True,
        min_price = min,
        max_price = max,
        subject = ''
    )

@router.get('/ads/subcategory/{subcategory_id}')
@template(template_file='products/products.pt')
async def show_ads_category(request: Request, subcategory_id: int, session: Annotated[AsyncSession, Depends(get_db_session)]):
    in_subcategories_view = False
    request_path = request.url.path
    if request_path.endswith(f'/subcategory/{subcategory_id}'):
        in_subcategories_view = True

    all_ads = await ad_service.get_subcategory_ads_asc(subcategory_id, session)
    min, max = get_min_max_price(all_ads)

    return await ViewModel(
        all_categories = await category_service.get_all_categories(session),
        all_ads = all_ads,
        all_cities = await ad_service.get_cities_by_subcategory(subcategory_id, session),
        all_subcategories = [],
        in_subcategories_view = in_subcategories_view,
        in_categories_view = True,
        min_price = min,
        max_price = max,
        subject = ''
    )

@router.get('/ads/search')
@template(template_file = 'products/products.pt')
async def search_by_title(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    title: str | None = '',
    description: str | None = None,
):
    ads_found = await ad_service.get_ads_by_title_or_description(session, title, description)
    min, max = 0, 0
    if ads_found:
        min, max = get_min_max_price(ads_found)

    return await ViewModel(
        all_categories = await category_service.get_all_categories(session),
        all_ads = ads_found,
        all_cities = await ad_service.get_cities_with_ads_by_text(title, session),
        all_subcategories = [],
        in_subcategories_view = False,
        in_categories_view = False,
        min_price = min,
        max_price = max,
        subject = title
    )

@router.get('/new/ad', dependencies = [Depends(requires_authentication)])
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

@router.post('/new/ad', dependencies = [Depends(requires_authentication)])
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
    
    if user:= await get_user_account_by_id(vm.user_id, session):
        if not user.phone_number and len(vm.phone) == 0:
            vm.error, vm.error_msg = True, 'Insira um número de telemóvel com o seguinte formato: +351 123 456 789 ou 123 456 789'


    if not vm.error:
        vm.files = []
        for file in files:
            url = upload_image(file)
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

@router.delete('/ad/{ad_id}', dependencies = [Depends(requires_authentication)])
async def delete_ad(ad_id: int, session: Annotated[AsyncSession, Depends(get_db_session)]):
    ad = await ad_service.set_deleted_status(ad_id, session)
    return {'msg': 'Ad deleted successfully!'}