from decimal import Decimal as dec
from enum import Enum
from typing import List
from sqlalchemy import and_, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from models import ad, user
from models.category import Category
from models.subcategory import Subcategory

# CREATE
async def insert_feature(
    brand: str, 
    auth: str, 
    condition_id: int, 
    session: AsyncSession
) -> int:
    feature = ad.Feature(
            brand = brand,
            authenticity = auth,
            condition_id = condition_id
        )
    session.add(feature)
    await session.commit()
    await session.refresh(feature)
    new_feature_id = feature.id
    return new_feature_id

async def insert_ad_address(
    country: str, 
    city: str, 
    session: AsyncSession
) -> int:
    if ad_address:= await get_existing_address(country, city, session):
        return ad_address.id
    
    ad_address = ad.AdAddress(
        country = country,
        city = city
    )
    session.add(ad_address)
    await session.commit()
    await session.refresh(ad_address)
    new_address_id = ad_address.id
    return new_address_id

async def insert_ad_images(
    ad_id: int, 
    images: List, 
    session: AsyncSession
) -> None:
    for image in images:
        ad_image = ad.AdImage(
            image_name = image['filename'],
            image_path_url = image['file_path'],
            ad_id = ad_id
        )
        session.add(ad_image)
    await session.commit()

async def insert_ad(
    title: str, 
    subcategory_id: int, 
    brand: str, 
    condition_id: int, 
    price: dec, 
    is_negotiable: bool, 
    description: str, 
    images: List, 
    user_id: int, 
    country: str, 
    city: str, 
    ad_status_id: int, 
    authenticity: str, 
    session: AsyncSession
) -> None:
    db_feature_id = await insert_feature(
        brand, 
        authenticity, 
        condition_id, 
        session
    )
    db_ad_address_id = await insert_ad_address(country, city, session)
    db_ad = ad.Ad(
        title = title,
        ad_description = description,
        price = price,
        views = 0,
        is_negotiable = 1 if is_negotiable else 0,
        user_id = user_id,
        subcategory_id = subcategory_id,
        status_id = ad_status_id,
        feature_id = db_feature_id,
        ad_address_id = db_ad_address_id
    )
    
    session.add(db_ad)
    await session.commit()
    await session.refresh(db_ad)
    await insert_ad_images(db_ad.id, images, session)

# READ
async def get_all_ad_conditions(session: AsyncSession) -> List[ad.AdCondition]:
    query = await session.execute(select(ad.AdCondition))
    ad_conditions = query.unique().scalars().all()

    return ad_conditions

async def get_all_features(session: AsyncSession) -> List[ad.Feature]:
    query = await session.execute(select(ad.Feature))
    features = query.unique().scalars().all()

    return features

async def get_existing_address(
    country: str, 
    city: str, 
    session: AsyncSession
) -> ad.AdAddress:
    query = await session.execute(select(ad.AdAddress)
        .where(
            and_(
                ad.AdAddress.city == city,
                ad.AdAddress.country == country
            )
        )
    )
    address = query.scalar_one_or_none()
    
    return address


async def get_all_ads(session: AsyncSession) -> List[ad.Ad]:
    query = await session.execute(select(ad.Ad)
        .where(ad.Ad.status_id == AdStatusEnum.ACTIVE.value)
        .order_by(ad.Ad.title.asc())    
    )
    ads = query.unique().scalars().all()

    return ads

async def get_3_ads(current_ad: ad.Ad, session: AsyncSession) -> List[ad.Ad]:
    query = await session.execute(select(ad.Ad).
    where(
        and_(
            ad.Ad.subcategory_id == current_ad.subcategory_id,
            ad.Ad.id != current_ad.id,
            ad.Ad.status_id == AdStatusEnum.ACTIVE.value
        )
    ).limit(3))
    ads = query.unique().scalars().all()

    return ads

async def get_ad_by_id(session: AsyncSession, ad_id: int) -> ad.Ad | None:
    query = await session.execute(
        select(ad.Ad)
        .where(
            and_(
                ad.Ad.id == ad_id, 
                ad.Ad.status_id == AdStatusEnum.ACTIVE.value
            )
        )
    )
    adv = query.unique().scalar_one_or_none()
    
    return adv

async def get_one_ad_without_criteria(
    session: AsyncSession, 
    ad_id: int
) -> ad.Ad | None:
    query = await session.execute(
        select(ad.Ad)
        .where(ad.Ad.id == ad_id)
    )
    adv = query.unique().scalar_one_or_none()
        
    return adv

async def get_ads_by_user_id(session: AsyncSession, user_id) -> List[ad.Ad]:
    query = await session.execute(select(ad.Ad)
            .join(ad.Ad.user)
            .where(
                and_(
                    ad.Ad.user_id == user_id
                )
            )
    )   
    ads_by_user_id = query.unique().scalars().all()
    
    return ads_by_user_id

async def get_ads_by_user_id_and_status(
    session: AsyncSession, 
    user_id, 
    status_id
) -> List[ad.Ad]:
    query = await session.execute(select(ad.Ad)
            .join(ad.Ad.user)
            .where(and_(
                    ad.Ad.user_id == user_id,
                    ad.Ad.status_id == status_id
                )
            )
    )   
    ads_by_user_id = query.unique().scalars().all()
    
    return ads_by_user_id

async def get_favorite_ads_by_user_id_and_status(
    session: AsyncSession, 
    user_id: int, 
    status_id: int
) -> List[ad.Ad]:
    subquery = await session.execute(select(user.Favourite.ad_id)
            .where(user.Favourite.user_id == user_id)
    )
    subquery_result = subquery.unique().scalars().all()
    
    query = await session.execute(select(ad.Ad)
            .join(ad.Ad.users_favourited)
            .where(and_(
                    ad.Ad.status_id == status_id,
                    ad.Ad.id.in_(subquery_result)
                )
            )
    )   
    favorite_ads_by_user_id_and_status = query.unique().scalars().all()
    
    return favorite_ads_by_user_id_and_status

async def get_ad_count_by_user_id(
    session: AsyncSession, 
    user_id: int
) -> List[ad.Ad]:
    query = await session.execute(select(func.count(ad.Ad.id))
            .join(ad.Ad.user)
            .where(ad.Ad.user_id == user_id)
    )   
    ads_by_user_id = query.scalar_one_or_none()
    
    return ads_by_user_id

async def get_ad_count_by_user_id_and_status(
    session: AsyncSession, 
    user_id: int, 
    status_id: int
) -> List[ad.Ad]:
    query = await session.execute(select(func.count(ad.Ad.id))
            .join(ad.Ad.user)
            .where(
                and_(
                    ad.Ad.user_id == user_id,
                    ad.Ad.status_id == status_id
                    )
            )
    )   
    ads_by_user_id = query.scalar_one_or_none()
    
    return ads_by_user_id

async def get_ads_by_asc(category_id, session: AsyncSession) -> List[ad.Ad]:
    query = await session.execute(select(ad.Ad)
            .join(ad.Ad.subcategory)
            .join(Subcategory.category)
            .where(
                and_(
                    Category.id == category_id,
                    ad.Ad.status_id == AdStatusEnum.ACTIVE.value
                    )
                )
            .order_by(ad.Ad.promo_id.desc(), ad.Ad.title.asc()))
    asc_ads = query.unique().scalars().all()
    return asc_ads

async def get_subcategory_ads_asc(
    subcategory_id: int, 
    session: AsyncSession
) -> List[ad.Ad]:
    query = await session.execute(select(ad.Ad)
            .where(
                and_(
                    ad.Ad.subcategory_id == subcategory_id,
                    ad.Ad.status_id == AdStatusEnum.ACTIVE.value
                    )
                )
            .order_by(ad.Ad.promo_id.desc(), ad.Ad.title.asc()))
    asc_ads = query.unique().scalars().all()
    return asc_ads

async def get_ads_by_status(session: AsyncSession, status: str) -> List[ad.Ad]:
    query = await session.execute(select(ad.Ad)
        .join(ad.Ad.ad_status)
        .where(ad.AdStatus.status_name == status)
    )
    ads_by_status = query.unique().scalars().all()
    
    return ads_by_status

async def get_paid_promos(session: AsyncSession) -> List[ad.Promo]:
    query = await session.execute(
        select(ad.Promo)
        .where(ad.Promo.promo_price != None)
        .order_by(ad.Promo.promo_price.desc())
    )
    paid_promos = query.unique().scalars().all()
    assert len(paid_promos) == 2

    return paid_promos

async def get_promo_by_id(
    promo_id: int, 
    session: AsyncSession
) -> ad.Promo:
    query = await session.execute(
        select(ad.Promo)
        .where(ad.Promo.id == promo_id)
    )
    promo = query.scalar_one_or_none()
    assert isinstance(promo, ad.Promo)

    return promo

async def get_popular_ads(
    session: AsyncSession, 
    limit: int = 8
) -> List[ad.Ad]:
    query = await session.execute(select(ad.Ad)
        .join(ad.Ad.ad_status)
        .where(ad.Ad.status_id == AdStatusEnum.ACTIVE.value)
        .order_by(ad.Ad.views.desc())
        .limit(limit)
    )
    popular_ads = query.unique().scalars().all()
    
    return popular_ads

async def get_ads_by_creation_date(
    session: AsyncSession, 
    limit: int = 8
) -> List[ad.Ad]:
    query = await session.execute(select(ad.Ad)
        .where(ad.Ad.status_id == AdStatusEnum.ACTIVE.value)
        .order_by(ad.Ad.created_at.desc())
        .limit(limit)
    )
    recent_ads = query.unique().scalars().all()

    return recent_ads

async def get_ads_by_title_or_description(
    session: AsyncSession, title: str,
    description: str,
):
    filters = []
    if title:
        filters.append(ad.Ad.title.like(f'%{title}%'))
    if description:
        filters.append(ad.Ad.ad_description.like(f'%{title}%'))

    query = select(ad.Ad).where(
                and_(ad.Ad.status_id == AdStatusEnum.ACTIVE.value),
                or_(*filters)
            ).order_by(ad.Ad.promo_id.desc(), ad.Ad.title.asc())

    ads_result = await session.execute(query)
    count_result = await session.execute(query)

    total_ads_found = len(count_result.unique().scalars().all())
    ads_found = ads_result.unique().scalars().all()

    return ads_found, total_ads_found

async def get_ads_by_criteria(
    session: AsyncSession,
    title: str,
    description: str,
    city: str,
    category_id: int = 0, 
    subcategory_id: int = 0,
    order_by: str = '',
    min_price: dec = 0,
    max_price: dec = 0,
    page: int = 1,
    items_per_page: int = 9
) -> List[ad.Ad]:
    filters = []
    filters.append(ad.Ad.status_id == AdStatusEnum.ACTIVE.value)
    if title and description:
        filter = or_(
            ad.Ad.title.like(f'%{title}%'), 
            ad.Ad.ad_description.like(f'%{title}%')
        )
        filters.append(filter)
    elif title:
        filters.append(ad.Ad.title.like(f'%{title}%'))
    if city:
        filters.append(ad.AdAddress.city == city)
    if category_id:
        filters.append(Category.id == category_id)
    if subcategory_id:
        filters.append(Subcategory.id == subcategory_id)
    if min_price and max_price:
        filters.append(ad.Ad.price.between(min_price, max_price))

    criteria = (ad.Ad.title.asc())
    has_criteria = False
    if order_by == 'asc':
        has_criteria = True
        criteria = (ad.Ad.title.asc())
    elif order_by == 'desc':
        has_criteria = True
        criteria = (ad.Ad.title.desc())
    elif order_by == 'recent':
        has_criteria = True
        criteria = (ad.Ad.created_at.desc())
    elif order_by == 'old':
        has_criteria = True
        criteria = (ad.Ad.created_at.asc())
    elif order_by == 'expensive':
        has_criteria = True
        criteria = (ad.Ad.price.desc())
    elif order_by == 'cheap':
        has_criteria = True
        criteria = (ad.Ad.price.asc())

    offset = (page - 1) * items_per_page

    query = (select(ad.Ad)
        .join(ad.Ad.address)
        .join(ad.Ad.subcategory)
        .join(Subcategory.category)
        .where(and_(*filters))
    )
    query_with_offset = query.offset(offset).limit(items_per_page)
    query_with_offset = query_with_offset.order_by(criteria)
    if not has_criteria:
        query_with_offset = query_with_offset.order_by(
            ad.Ad.promo_id.desc(), 
            ad.Ad.title.asc()
        )

    partial_result = await session.execute(query_with_offset)
    partial_count_result = await session.execute(query)
    ads_by_criteria = partial_result.unique().scalars().all()
    total_ads_by_criteria = len(partial_count_result.unique().scalars().all())

    return ads_by_criteria, total_ads_by_criteria

async def get_locations_by_total_ads(
    session: AsyncSession
) -> List[ad.AdAddress]:
    query = await session.execute(
        select(ad.AdAddress, func.count(ad.Ad.ad_address_id))
        .join(ad.Ad.address)
        .where(ad.Ad.status_id == AdStatusEnum.ACTIVE.value)
        .group_by(ad.AdAddress.city)
        .order_by(func.count(ad.Ad.ad_address_id).desc())
        .limit(3)
        .options(selectinload(ad.AdAddress.ads))
    )
    addresses_with_counts = query.unique().all()
    handled_models = []
    for address, count in addresses_with_counts:
        setattr(address, 'count_total_ads', count)
        handled_models.append(address)

    return handled_models

async def get_cities_with_ads_by_text(
    text: str, 
    session: AsyncSession
) -> List[ad.AdAddress]:
    query = await session.execute(
        select(ad.AdAddress.city)
        .where(
            and_(ad.Ad.status_id == AdStatusEnum.ACTIVE.value), 
            or_(ad.Ad.title.like(f'%{text}%'),
                ad.Ad.ad_description.like(f'%{text}%')
            )
        )
        .join(ad.AdAddress.ads)
        .group_by(ad.AdAddress.city)
        .order_by(func.count(ad.Ad.ad_address_id).desc())
    )
    cities_with_ads = query.unique().scalars().all()
    
    return cities_with_ads

async def get_cities_by_category(
    category_id: int, 
    session: AsyncSession
) -> List[ad.AdAddress]:
    query = await session.execute(select(ad.AdAddress.city)
        .join(ad.Ad.address)
        .join(ad.Ad.subcategory)
        .join(Subcategory.category)
        .where(
                and_(
                    Category.id == category_id,
                    ad.Ad.status_id == AdStatusEnum.ACTIVE.value
                    )
                )
        .group_by(ad.AdAddress.city)
    )
    cities = query.unique().scalars().all()

    return cities

async def get_cities_by_subcategory(
    subcategory_id: int, 
    session: AsyncSession
) -> List[ad.AdAddress]:
    query = await session.execute(select(ad.AdAddress.city)
        .join(ad.Ad.address)
        .join(ad.Ad.subcategory)
        .where(
            and_(
                ad.Ad.subcategory_id == subcategory_id,
                ad.Ad.status_id == AdStatusEnum.ACTIVE.value
                )
            )
        .group_by(ad.AdAddress.city)
    )
    cities = query.unique().scalars().all()

    return cities

def filter_ads_by_status(ads_list: List[ad.Ad], status_id: int) -> List[ad.Ad]:
    return [ad for ad in ads_list if ad.status_id == status_id]

# UPDATE
async def update_promo_id(
    ad_id: int, 
    new_promo_id: int, 
    session: AsyncSession
) -> None:
    ad = await get_ad_by_id(session, ad_id)
    ad.promo_id = new_promo_id
    await session.commit()

async def update_views_count(ad: ad.Ad, session: AsyncSession) -> ad.Ad:
    ad.views += 1
    await session.commit()
    await session.refresh(ad)

    return ad

# DELETE
async def set_deleted_status(ad_id: int, session: AsyncSession) -> ad.Ad:
    ad = await get_one_ad_without_criteria(session, ad_id)
    ad.status_id = AdStatusEnum.DELETED.value
    await session.commit()
    await session.refresh(ad)
    return ad

class AdStatusEnum(Enum):
    ACTIVE = 1
    INACTIVE = 2
    EXPIRED = 3
    SOLD = 4
    DELETED = 5