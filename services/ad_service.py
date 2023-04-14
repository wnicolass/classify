from decimal import Decimal as dec
from typing import List, Tuple
from sqlalchemy import and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from models import ad
from models.category import Category
from models.subcategory import Subcategory

async def get_all_features(session: AsyncSession) -> List[ad.Feature]:
    query = await session.execute(select(ad.Feature))
    features = query.unique().scalars().all()

    return features

async def get_all_ad_conditions(session: AsyncSession) -> List[ad.AdCondition]:
    query = await session.execute(select(ad.AdCondition))
    ad_conditions = query.unique().scalars().all()

    return ad_conditions

async def insert_feature(brand: str, auth: str, condition_id: int, session: AsyncSession) -> int:
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

async def insert_ad_address(country: str, city: str, session: AsyncSession) -> int:
    ad_address = ad.AdAddress(
        country = country,
        city = city
    )
    session.add(ad_address)
    await session.commit()
    await session.refresh(ad_address)
    new_address_id = ad_address.id
    return new_address_id

async def insert_ad_images(ad_id: int, images: List, session: AsyncSession) -> None:
    for image in images:
        ad_image = ad.AdImage(
            image_name = image['filename'],
            image_path_url = image['file_path'],
            ad_id = ad_id
        )
        session.add(ad_image)
    await session.commit()

async def insert_ad(title: str, subcategory_id: int, brand: str, condition_id: int, price: dec, is_negotiable: bool, description: str, images: List, user_id: int, country: str, city: str, ad_status_id: int, authenticity: str, session: AsyncSession) -> None:
    db_feature_id = await insert_feature(brand, authenticity, condition_id, session)
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

async def get_all_ads(session: AsyncSession) -> List[ad.Ad]:
    query = await session.execute(select(ad.Ad))
    ads = query.unique().scalars().all()

    return ads

async def get_3_ads(current_ad: ad.Ad, session: AsyncSession) -> List[ad.Ad]:
    query = await session.execute(select(ad.Ad).
    where(
        and_(
            ad.Ad.subcategory_id == current_ad.subcategory_id,
            ad.Ad.id != current_ad.id
        )
    ).limit(3))
    ads = query.unique().scalars().all()

    return ads

async def get_ad_by_id(session: AsyncSession, ad_id: int) -> ad.Ad | None:
    query = await session.execute(select(ad.Ad).where(ad.Ad.id == ad_id))
    adv = query.unique().scalar_one_or_none()
    
    return adv

# ADS BY USER
async def get_ads_by_user_id(session: AsyncSession, user_id) -> List[ad.Ad]:
    query = await session.execute(select(ad.Ad)
            .join(ad.Ad.user)
            .where(ad.Ad.user_id == user_id)
    )   
    ads_by_user_id = query.unique().scalars().all()
    
    return ads_by_user_id

async def get_ads_by_user_id_and_status(session: AsyncSession, user_id, status_id) -> List[ad.Ad]:
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

async def get_ad_count_by_user_id(session: AsyncSession, user_id) -> List[ad.Ad]:
    query = await session.execute(select(func.count(ad.Ad.id))
            .join(ad.Ad.user)
            .where(ad.Ad.user_id == user_id)
    )   
    ads_by_user_id = query.scalar_one_or_none()
    
    return ads_by_user_id

async def get_ad_count_by_user_id_and_status(session: AsyncSession, user_id, status_id) -> List[ad.Ad]:
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
            .where(Category.id == category_id)
            .order_by(ad.Ad.title.asc()))
    asc_ads = query.scalars().all()

    return asc_ads

async def get_ads_by_desc(category_id, session: AsyncSession) -> List[ad.Ad]:
    query = await session.execute(select(ad.Ad)
            .join(ad.Ad.subcategory)
            .join(Subcategory.category)
            .where(Category.id == category_id)
            .order_by(ad.Ad.title.desc()))
    desc_ads = query.scalars().all()

    return desc_ads

# ADS BY CATEGORIES & SUBCATEGORIES
async def get_ads_by_category_id(session: AsyncSession, category_id) -> List[ad.Ad]:
    query = await session.execute(select(ad.Ad)
            .join(ad.Ad.subcategory)
            .join(Subcategory.category)
            .filter(Category.id == category_id)
    )   
    ads_by_category_id = query.unique().scalars().all()
    
    return ads_by_category_id

async def get_ads_by_category(session: AsyncSession, category_id: str, title: str) -> List[ad.Ad]:
    query = await session.execute(select(ad.Ad)
            .join(ad.Ad.subcategory)
            .join(Subcategory.category)
            .where(
                and_(
                    Category.id == category_id,
                    ad.Ad.title.like(f'%{title}%')
                )
            )
        )
    ads_by_category = query.unique().scalars().all()

    return ads_by_category

async def get_ads_by_subcategory_id(session: AsyncSession, subcategory_id) -> List[ad.Ad]:
    query = await session.execute(select(ad.Ad)
            .join(ad.Ad.subcategory)
            .where(Subcategory.id == subcategory_id)
    )
    ads_by_subcategory = query.unique().scalars().all()

    return ads_by_subcategory

async def get_ads_count_category(session: AsyncSession, category) -> List[List]:
    query = await session.execute(select(Category.category_name, func.count(ad.Ad.id))
            .join(ad.Ad.subcategory)
            .join(Subcategory.category)
            .filter(Category.category_name.like(f'%{category}%'))
    )
    ads_count_category = query.unique().scalars().all()

    return ads_count_category

# ADS BY STATUS
async def get_all_active_ads(session: AsyncSession) -> List[ad.Ad]:
    query = await session.execute(select(ad.Ad).filter(ad.AdStatus == 'active'))
    active_ads = query.unique().scalars().all()

    return active_ads

async def get_all_sold_ads(session: AsyncSession) -> List[ad.Ad]:
    query = await session.execute(select(ad.Ad).filter(ad.AdStatus == 'sold'))
    sold_ads = query.unique().scalars().all()

    return sold_ads

async def get_all_inactive_ads(session: AsyncSession) -> List[ad.Ad]:
    query = await session.execute(select(ad.Ad).filter(ad.AdStatus == 'inactive'))
    inactive_ads = query.unique().scalars().all()

    return inactive_ads

async def get_all_deleted_ads(session: AsyncSession) -> List[ad.Ad]:
    query = await session.execute(select(ad.Ad).filter(ad.AdStatus == 'deleted'))
    deleted_ads = query.unique().scalars().all()

    return deleted_ads

async def get_all_expired_ads(session: AsyncSession) -> List[ad.Ad]:
    query = await session.execute(select(ad.Ad).filter(ad.AdStatus == 'expired'))
    expired_ads = query.unique().scalars().all()

    return expired_ads

async def get_ads_by_status(session: AsyncSession, status: str) -> List[ad.Ad]:
    query = await session.execute(select(ad.Ad)
        .join(ad.Ad.ad_status)
        .where(ad.AdStatus.status_name == status)
    )
    ads_by_status = query.unique().scalars().all()
    
    return ads_by_status

async def get_popular_ads(session: AsyncSession, limit: int = 8) -> List[ad.Ad]:
    query = await session.execute(select(ad.Ad)
        .join(ad.Ad.ad_status)
        .where(ad.AdStatus.status_name == 'ativo')
        .order_by(ad.Ad.views.desc())
        .limit(limit)
    )
    popular_ads = query.unique().scalars().all()
    
    return popular_ads

# ADS BY USER INPUT
async def get_ads_by_price(session: AsyncSession, min: int, max: int) -> List[ad.Ad]:
    query = await session.execute(select(ad.Ad).filter(ad.Ad.price.between(min, max))
    )
    most_expensive_ads = query.unique().scalars().all()

    return most_expensive_ads

async def get_ads_by_location(session: AsyncSession, location: str, title: str) -> List[ad.Ad]:
    query = await session.execute(
        select(ad.Ad)
        .join(ad.AdAddress)
        .where(
            and_(
                ad.AdAddress.city == f'{location}',
                ad.Ad.title.like(f'%{title}%')
            )
        )
    )
    ads_by_location = query.unique().scalars().all()

    return ads_by_location

async def get_ads_by_creation_date(session: AsyncSession, limit: int = 8) -> List[ad.Ad]:
    query = await session.execute(select(ad.Ad)
        .order_by(ad.Ad.created_at.desc())
        .limit(limit)
    )
    recent_ads = query.unique().scalars().all()

    return recent_ads

async def get_ads_by_title(session: AsyncSession, title: str) -> List[ad.Ad]:
    query = await session.execute(
        select(ad.Ad)
        .where(ad.Ad.title.like(f'%{title}%'))
    )
    ads_by_title = query.unique().scalars().all()

    return ads_by_title

async def get_locations_by_total_ads(session: AsyncSession) -> List[ad.AdAddress]:
    query = await session.execute(select(ad.AdAddress, func.count(ad.Ad.ad_address_id))
        .join(ad.Ad.address)
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

async def get_ads_by_location_and_category(
    city: str, 
    category_id: int, 
    title: str, 
    session: AsyncSession
) -> List[ad.Ad]:
    query = await session.execute(
        select(ad.Ad)
        .join(ad.Ad.subcategory)
        .join(Subcategory.category)
        .join(ad.Ad.address)
        .where(
            and_(
                ad.Ad.title.like(f'%{title}%'),
                Category.id == category_id,
                ad.AdAddress.city == city
            )
        )
    )
    ads_found = query.unique().scalars().all()
    return ads_found

async def get_ads_by_description(session: AsyncSession, description: str) -> List[ad.Ad]:
    query = await session.execute(select(ad.Ad).filter(ad.Ad.ad_description.like(f'%{description}%')))
    ads_by_description = query.unique().scalars().all()

    return ads_by_description


async def get_ads_by_recency(session: AsyncSession) -> List[ad.Ad]:
    query = await session.execute(select(ad.Ad).order_by(ad.Ad.created_at).desc())
    recent_ads = query.unique().scalars().all()

    return recent_ads

async def get_ads_by_antiquity(category_id, session: AsyncSession) -> List[ad.Ad]:
    query = await session.execute(select(ad.Ad)
            .join(ad.Ad.subcategory)
            .join(Subcategory.category)
            .where(Category.id == category_id)
            .order_by(ad.Ad.created_at).asc())
    antique_ads = query.unique().scalars().all()

    return antique_ads

# RELATED WITH ADS
async def get_cities_with_ads(session: AsyncSession) -> List[ad.AdAddress]:
    query = await session.execute(
        select(ad.AdAddress)
        .join(ad.AdAddress.ads)
        .group_by(ad.AdAddress.city)
        .order_by(func.count(ad.Ad.ad_address_id).desc())
    )
    cities_with_ads = query.unique().scalars().all()
    
    return cities_with_ads
