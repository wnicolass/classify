from sqlalchemy import text
from config.database import Session

async def seed_data() -> None:
    async with Session() as db_session:
        await db_session.execute(text('CALL SeedData'))
        await db_session.commit()