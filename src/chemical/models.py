from sqlalchemy.orm import  Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound
from fastapi import HTTPException
from sqlalchemy import text, Integer, String, select

from src.models import TimestampMixin
from src.database import Base

class Chemical(TimestampMixin, Base):
    __tablename__ = "chemicals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True,
                                    autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    cas_number: Mapped[str] = mapped_column(String(100), nullable=False)
    quantity: Mapped[int] = mapped_column(nullable=False)
    unit: Mapped[str] = mapped_column(String(10), nullable=False)


    def __repr__(self) -> str:
        return f"Chemical id={self.id} name={self.name} cas_number={self.cas_number}"

    @classmethod
    async def create(cls, db: AsyncSession, **kwargs):
      transaction = cls(**kwargs)
      db.add(transaction)
      await db.commit()
      await db.refresh(transaction)
      return transaction

    @classmethod
    async def get(cls, db: AsyncSession, id: int):
      try:
        transaction = await db.get(cls, id)
      except NoResultFound:
        return None
      return transaction

    @classmethod
    async def get_all(cls, db: AsyncSession, limit: int = 10, offset: int = 0):
      return (await db.execute(select(cls).limit(limit).offset(offset))).scalars().all()

    @classmethod
    async def update(cls, db: AsyncSession, chemical_id: int, **kwargs):
      obj = await db.get(cls, chemical_id)
      if not obj:
        raise HTTPException(status_code=404, detail="Chemical not found")

      for key, value in kwargs.items():
        setattr(obj, key, value)

      db.add(obj)
      await db.commit()
      await db.refresh(obj)
      return obj

    @classmethod
    async def delete(cls, db: AsyncSession, chemical_id: int):
      obj = await db.get(cls, chemical_id)

      if not obj:
        raise HTTPException(status_code=404, detail="Chemical not found")
      obj_name = obj.name
      await db.delete(obj)
      await db.commit()
      return {"message": f"Chemical with id {obj_name} deleted successfully"}

    @classmethod
    async def get_by_id_raw(cls, db: AsyncSession, chemical_id: int):
      query = text("""
                   SELECT id, name, cas_number, quantity, unit, created_at, updated_at
                   FROM chemicals
                   WHERE id = :chemical_id
                   """)
      result = await db.execute(query, {"chemical_id": chemical_id})
      row = result.mappings().first()

      if not row:
        raise HTTPException(status_code=404, detail="Chemical not found")

      return row
