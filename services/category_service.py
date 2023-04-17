from typing import List
from sqlalchemy import and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.category import Category
from models.subcategory import Subcategory
from models.ad import Ad
from services.ad_service import AdStatusEnum

async def get_category_by_id(id: int, session: AsyncSession) -> Category | None:
    query = await session.execute(select(Category).where(Category.id == id))
    category = query.scalar_one_or_none()
    return category


async def get_category_by_name(name: str, session: AsyncSession) -> Category | None:
    query = await session.execute(select(Category).where(Category.category_name == name))
    category = query.scalar_one_or_none()
    return category

async def get_categories_by_asc(session: AsyncSession) -> List[Category]:
    query = await session.execute(select(Category).order_by(Category.category_name.asc()))
    asc_categories = query.scalars().all()

    return asc_categories

async def get_categories_by_desc(session: AsyncSession) -> List[Category]:
    query = await session.execute(select(Category).order_by(Category.category_name.desc()))
    desc_categories = query.scalars().all()

    return desc_categories

async def get_category_count(session: AsyncSession) -> int | None:
    query = await session.execute(select(func.count(Category.id)))
    category_count = query.scalar_one_or_none()
    return category_count


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


async def create_category(category_name: str, session: AsyncSession) -> Category | None:
    category = Category(
        category_name = category_name
    )
    
    session.add(category)
    await session.commit()
    await session.refresh(category)
    return category



async def get_subcategory_by_id(id: int, session: AsyncSession) -> Subcategory | None:
    query = await session.execute(select(Subcategory).where(Subcategory.id == id))
    subcategory = query.scalar_one_or_none()
    return subcategory


async def get_subcategory_by_name(name: str, session: AsyncSession) -> Subcategory | None:
    query = await session.execute(select(Subcategory).where(Subcategory.subcategory_name == name))
    subcategory = query.scalar_one_or_none()
    return subcategory

async def get_subcategory_by_category_id(category_id: int, session: AsyncSession) -> List[Subcategory]:
    query = await session.execute(select(Subcategory).where(Subcategory.category_id == category_id))
    subcategories = query.unique().scalars().all()

    return subcategories

async def get_subcategory_count(session: AsyncSession) -> int | None:
    query = await session.execute(select(func.count(Subcategory.id)))
    subcategory_count = query.scalar_one_or_none()
    return subcategory_count


async def get_all_subcategories(session: AsyncSession) -> List[Subcategory]:
    query = await session.execute(select(Subcategory))
    all_subcategories = query.scalars().all()
    return all_subcategories


async def create_subcategory(subcategory_name: str, category_id, session: AsyncSession) -> Subcategory | None:
    subcategory = Subcategory(
        subcategory_name = subcategory_name,
        category_id = category_id
    )
    
    session.add(subcategory)
    await session.commit()
    await session.refresh(subcategory)
    return subcategory