from typing import List
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
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

async def get_all_ads(session: AsyncSession) -> List[ad.Ad]:
    query = await session.execute(select(ad.Ad))
    ads = query.unique().scalars().all()

    return ads

# ADS BY CATEGORIES & SUBCATEGORIES
async def get_ads_by_category(session: AsyncSession, category) -> List[ad.Ad]:
    query = await session.execute(select(Category.category_name)
            .join(ad.Ad.subcategory)
            .join(Subcategory.category)
            .filter(Category.category_name.like(f'%{category}%'))
    )
    ads_by_category = query.unique().scalars().all()

    return ads_by_category

async def get_ads_by_subcategory(session: AsyncSession, subcategory) -> List[ad.Ad]:
    query = await session.execute(select(ad.Ad)
            .join(ad.Ad.subcategory)
            .filter(Subcategory.subcategory_name.like(f'%{subcategory}%'))
    )
    ads_by_subcategory = query.unique().scalars().all()

    return ads_by_subcategory

async def get_ads_count_category(session: AsyncSession, category) -> List[str, int]:
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

async def get_popular_ads(session: AsyncSession, limit: int = 10) -> List[ad.Ad]:
    query = await session.execute(select(ad.Ad).filter(ad.AdStatus == 'active')
            .having(func.count(ad.Ad.views) >= 100)
            .order_by(func.count(ad.Ad.views).desc())
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

async def get_ads_by_location(session: AsyncSession, location: str) -> List[ad.Ad]:
    query = await session.execute(select(ad.Ad).filter(ad.AdAddress.city.like(f'%{location}%')))
    ads_by_location = query.unique().scalars().all()

    return ads_by_location

async def get_ads_by_title(session: AsyncSession, title: str) -> List[ad.Ad]:
    query = await session.execute(select(ad.Ad).filter(ad.Ad.title.like(f'%{title}%')))
    ads_by_title = query.unique().scalars().all()

    return ads_by_title

async def get_ads_by_description(session: AsyncSession, description: str) -> List[ad.Ad]:
    query = await session.execute(select(ad.Ad).filter(ad.Ad.ad_description.like(f'%{description}%')))
    ads_by_description = query.unique().scalars().all()

    return ads_by_description


async def get_ads_by_recency(session: AsyncSession) -> List[ad.Ad]:
    query = await session.execute(select(ad.Ad).order_by(ad.Ad.created_at).desc())
    recent_ads = query.unique().scalars().all()

    return recent_ads