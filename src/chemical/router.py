import asyncpg
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.chemical import schemas
from src.chemical.models import Chemical, InventoryLog
from src.database import get_db, get_pg_pool

router = APIRouter(prefix="/chemicals", tags=["chemical"])


@router.get("/", response_model=schemas.PaginatedChemicalSchemaOut)
async def get_chemicals(
  limit: int = Query(10, ge=1, le=100),
  offset: int = Query(0, ge=0),
  db: AsyncSession = Depends(get_db),
):
  chemicals = await Chemical.get_all(db, limit, offset)
  return chemicals


@router.post("/create", response_model=schemas.ChemicalSchemaOut)
async def create_chemicals(
  chemical: schemas.ChemicalSchemaIn, db: AsyncSession = Depends(get_db)
):
  chemical = await Chemical.create(db, **chemical.model_dump())
  return chemical


@router.put("/update/{id}", response_model=schemas.ChemicalSchemaOut)
async def update_chemicals(
  id: int, chemical: schemas.ChemicalSchemaIn, db: AsyncSession = Depends(get_db)
):
  chemical = await Chemical.update(db, id, **chemical.model_dump())
  return chemical


@router.delete("/delete/{id}", status_code=status.HTTP_200_OK)
async def delete_chemical(id: int, db: AsyncSession = Depends(get_db)):
  return await Chemical.delete(db, id)


@router.get("/{id}", response_model=schemas.ChemicalSchemaOut)
async def get_chemical_by_id(id: int, pool: asyncpg.Pool = Depends(get_pg_pool)):
  return await Chemical.get_by_id_raw(pool, id)


@router.get("/{id}/logs", response_model=schemas.PaginatedInventoryLogSchemaOut)
async def get_chemical_logs(
  id: int,
  limit: int = Query(10, ge=1, le=100),
  offset: int = Query(0, ge=0),
  pool: asyncpg.Pool = Depends(get_pg_pool),
):
  return await InventoryLog.get_logs_by_chemical_raw(pool, id, limit, offset)


@router.post("/{id}/log", response_model=schemas.InventoryLogSchemaOut)
async def create_chemical_log(
  id: int, log: schemas.InventoryLogSchemaIn, db: AsyncSession = Depends(get_db)
):
  # Check if chemical exists
  chemical = await db.get(Chemical, id)
  if not chemical:
    raise HTTPException(status_code=404, detail="Chemical not found")

  # Create log
  log_entry = await InventoryLog.create_log(
    db, chemical_id=id, action_type=log.action_type, quantity=log.quantity
  )
  return log_entry
