from decimal import Decimal as dec
from typing import List
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models import ad

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



async def insert_ad(title: str, subcategory_id: int, brand: str, authenticity: str, condition_id: int, price: dec, is_negotiable: bool, description: str, images: List, user_id: int, country: str, city: str, ad_status_id: int, session: AsyncSession) -> None:
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

