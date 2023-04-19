from typing import List
from sqlalchemy import and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.category import Category
from models.subcategory import Subcategory
from models.ad import Ad
from services.ad_service import AdStatusEnum

async def get_all_categories(session: AsyncSession) -> List[Category]:
    query = await session.execute(select(
            Category)
            .join(Category.subcategories)
            .outerjoin(Ad, (Subcategory.id == Ad.subcategory_id) & (Ad.status_id == AdStatusEnum.ACTIVE.value))
            .group_by(Category.id)
            .order_by(func.count(Ad.id).desc())
    )
    all_categories = query.unique().scalars().all()
    
    return all_categories

async def popular_categories(session: AsyncSession) -> List[Category]:
    query = await session.execute(select(
            Category)
            .join(Category.subcategories)
            .join(Subcategory.ads)
            .group_by(Category.id)
            .order_by(func.count(Ad.id).desc())
            .order_by(Category.category_name)
            .limit(10)
    )
    popular_categories = query.unique().scalars().all()
    return popular_categories

async def get_subcategory_by_category_id(category_id: int, session: AsyncSession) -> List[Subcategory]:
    query = await session.execute(select(Subcategory).where(Subcategory.category_id == category_id))
    subcategories = query.unique().scalars().all()

    return subcategories

async def get_category_by_subcategory_id(subcategory_id: int, session: AsyncSession) -> Category:
    query = await session.execute(select(Category)
        .join(Category.subcategories)
        .where(Subcategory.id == subcategory_id)
    )
    category = query.unique().scalar_one_or_none()

    return category.id