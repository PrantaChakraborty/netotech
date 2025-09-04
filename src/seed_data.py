import asyncio

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.chemical.models import Chemical
from src.database import SQL_ALCHEMY_DB_URL

# Build async database URL
ASYNC_DB_URL = SQL_ALCHEMY_DB_URL

# Async engine + session
engine = create_async_engine(ASYNC_DB_URL, echo=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def seed():
  chemicals_data = [
    {"name": "Water", "cas_number": "7732-18-5", "quantity": 100, "unit": "L"},
    {"name": "Carbon Dioxide", "cas_number": "124-38-9", "quantity": 50, "unit": "kg"},
    {"name": "Methane", "cas_number": "74-82-8", "quantity": 200, "unit": "m³"},
  ]

  async with AsyncSessionLocal() as session:
    # Check if already seeded
    result = await Chemical.get_all(session)
    if result["total"] != 0:
      return

  # Call create in separate sessions for atomic insert
  for data in chemicals_data:
    async with AsyncSessionLocal() as session:
      await Chemical.create(session, **data)


if __name__ == "__main__":
  asyncio.run(seed())
