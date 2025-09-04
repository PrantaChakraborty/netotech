from datetime import datetime, timezone
from enum import Enum as PyEnum

import asyncpg
from fastapi import HTTPException
from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, func, select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base
from src.models import TimestampMixin


class ActionType(str, PyEnum):
  add = "add"
  remove = "remove"
  update = "update"


class Chemical(TimestampMixin, Base):
  __tablename__ = "chemicals"

  id: Mapped[int] = mapped_column(
    Integer, primary_key=True, index=True, autoincrement=True
  )
  name: Mapped[str] = mapped_column(String(100), nullable=False)
  cas_number: Mapped[str] = mapped_column(String(100), nullable=False)
  quantity: Mapped[int] = mapped_column(nullable=False)
  unit: Mapped[str] = mapped_column(String(10), nullable=False)
  inventory_logs: Mapped[list["InventoryLog"]] = relationship(
    "InventoryLog",
    back_populates="chemical",
    cascade="all, delete-orphan",
  )

  def __repr__(self) -> str:
    return f"Chemical id={self.id} name={self.name} cas_number={self.cas_number}"

  @classmethod
  async def create(cls, db: AsyncSession, **kwargs):
    async with db.begin():  # atomic transaction
      chemical = cls(**kwargs)
      db.add(chemical)
      await db.flush()
      # create log in same session
      await InventoryLog.create_log(
        db=db,
        chemical_id=chemical.id,
        action_type=ActionType.add,
        quantity=chemical.quantity,
        is_atomic=True,
      )
    await db.refresh(chemical)

    return chemical

  @classmethod
  async def get(cls, db: AsyncSession, id: int):
    try:
      transaction = await db.get(cls, id)
    except NoResultFound:
      return None
    return transaction

  @classmethod
  async def get_all(cls, db: AsyncSession, limit: int = 10, offset: int = 0):
    total_result = await db.execute(select(func.count()).select_from(cls))
    total = total_result.scalar()

    # Get paginated results
    result = await db.execute(select(cls).limit(limit).offset(offset))
    chemicals = result.scalars().all()

    return {
      "total": total,
      "limit": limit,
      "offset": offset,
      "results": chemicals,
    }

  @classmethod
  async def update(cls, db: AsyncSession, chemical_id: int, **kwargs):
    async with db.begin():
      obj = await db.get(cls, chemical_id)
      if not obj:
        raise HTTPException(status_code=404, detail="Chemical not found")

      for key, value in kwargs.items():
        setattr(obj, key, value)
      db.add(obj)
      await db.flush()
      # create log in same session
      await InventoryLog.create_log(
        db=db,
        chemical_id=obj.id,
        action_type=ActionType.update,
        quantity=obj.quantity,
        is_atomic=True,
      )
    await db.refresh(obj)
    return obj

  @classmethod
  async def delete(cls, db: AsyncSession, chemical_id: int):
    async with db.begin():
      obj = await db.get(cls, chemical_id)

      if not obj:
        raise HTTPException(status_code=404, detail="Chemical not found")
      obj_name = obj.name
      await InventoryLog.create_log(
        db=db,
        chemical_id=obj.id,
        action_type=ActionType.remove,
        quantity=obj.quantity,
        is_atomic=True,
      )
      await db.delete(obj)
    return {"message": f"Chemical with id {obj_name} deleted successfully"}

  @classmethod
  async def get_by_id_raw(cls, pool: asyncpg.Pool, chemical_id: int):
    query = """
            SELECT id, name, cas_number, quantity, unit, created_at, updated_at
            FROM chemicals
            WHERE id = $1 \
            """
    async with pool.acquire() as conn:
      row = await conn.fetchrow(query, chemical_id)

    if not row:
      raise HTTPException(status_code=404, detail="Chemical not found")

    # Convert asyncpg Record to dict
    return dict(row)


class InventoryLog(Base):
  __tablename__ = "inventory_logs"

  id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
  chemical_id: Mapped[int] = mapped_column(ForeignKey("chemicals.id"))
  action_type: Mapped[ActionType] = mapped_column(
    Enum(ActionType, name="actiontype", native_enum=False), nullable=False
  )
  quantity: Mapped[int] = mapped_column(nullable=False)
  timestamp: Mapped[datetime] = mapped_column(
    DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
  )

  chemical: Mapped["Chemical"] = relationship(
    "Chemical",
    back_populates="inventory_logs",
  )

  @classmethod
  async def create_log(
    cls,
    db: AsyncSession,
    chemical_id: int,
    action_type: str | ActionType,
    quantity: int,
    is_atomic: bool = False,
  ):
    # Convert string to enum if needed
    if isinstance(action_type, str):
      action_type = ActionType(action_type)

    log_entry = cls(chemical_id=chemical_id, action_type=action_type, quantity=quantity)
    db.add(log_entry)
    if not is_atomic:
      await db.commit()
      await db.refresh(log_entry)

    return log_entry

  @classmethod
  async def get_logs_by_chemical_raw(
    cls, pool: asyncpg.Pool, chemical_id: int, limit: int = 10, offset: int = 0
  ):
    """Fetch logs for a chemical using a raw asyncpg query."""
    query = """
            SELECT il.id,
                   il.action_type,
                   il.quantity,
                   il.timestamp,
                   c.id AS chemical_id,
                   c.name,
                   c.cas_number,
                   c.unit
            FROM inventory_logs il
                     JOIN chemicals c ON il.chemical_id = c.id
            WHERE il.chemical_id = $1
            ORDER BY il.timestamp DESC
                LIMIT $2
            OFFSET $3
            """
    count_query = """
                  SELECT COUNT(*)
                  FROM inventory_logs
                  WHERE chemical_id = $1 \
                  """
    async with pool.acquire() as conn:
      rows = await conn.fetch(query, chemical_id, limit, offset)
      total = await conn.fetchval(count_query, chemical_id)
    return {
      "total": total,
      "limit": limit,
      "offset": offset,
      "results": [dict(row) for row in rows],
    }
