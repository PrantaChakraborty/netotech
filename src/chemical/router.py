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
  """Get paginated list of chemicals.

  Args:
      limit (int, optional): Maximum number of items to return. Defaults to 10.
      offset (int, optional): Number of items to skip. Defaults to 0.
      db (AsyncSession): Database session dependency.

  Returns:
      PaginatedChemicalSchemaOut: Paginated list of chemicals.
  """

  chemicals = await Chemical.get_all(db, limit, offset)
  return chemicals


@router.post("/", response_model=schemas.ChemicalSchemaOut)
async def create_chemicals(
  chemical: schemas.ChemicalSchemaIn, db: AsyncSession = Depends(get_db)
):
  """Create a new chemical.

  Args:
      chemical (ChemicalSchemaIn): Chemical data to create.
      db (AsyncSession): Database session dependency.

  Returns:
      ChemicalSchemaOut: Created chemical data.
  """
  chemical = await Chemical.create(db, **chemical.model_dump())
  return chemical


@router.put("/{id}", response_model=schemas.ChemicalSchemaOut)
async def update_chemicals(
  id: int, chemical: schemas.ChemicalSchemaIn, db: AsyncSession = Depends(get_db)
):
  """Update an existing chemical.

  Args:
      id (int): ID of the chemical to update.
      chemical (ChemicalSchemaIn): Updated chemical data.
      db (AsyncSession): Database session dependency.

  Returns:
      ChemicalSchemaOut: Updated chemical data.
  """
  chemical = await Chemical.update(db, id, **chemical.model_dump())
  return chemical


@router.delete("/{id}", status_code=status.HTTP_200_OK)
async def delete_chemical(id: int, db: AsyncSession = Depends(get_db)):
  """Delete a chemical by ID.

  Args:
      id (int): ID of the chemical to delete.
      db (AsyncSession): Database session dependency.

  Returns:
      dict: Success message.
  """
  return await Chemical.delete(db, id)


@router.get("/{id}", response_model=schemas.ChemicalSchemaOut)
async def get_chemical_by_id(id: int, pool: asyncpg.Pool = Depends(get_pg_pool)):
  """Get a chemical by ID.

  Args:
      id (int): ID of the chemical to retrieve.
      pool (asyncpg.Pool): Database connection pool.

  Returns:
      ChemicalSchemaOut: Chemical data.
  """
  return await Chemical.get_by_id_raw(pool, id)


@router.get("/{id}/logs", response_model=schemas.PaginatedInventoryLogSchemaOut)
async def get_chemical_logs(
  id: int,
  limit: int = Query(10, ge=1, le=100),
  offset: int = Query(0, ge=0),
  pool: asyncpg.Pool = Depends(get_pg_pool),
):
  """Get paginated logs for a specific chemical.

  Args:
      id (int): ID of the chemical.
      limit (int, optional): Maximum number of items to return. Defaults to 10.
      offset (int, optional): Number of items to skip. Defaults to 0.
      pool (asyncpg.Pool): Database connection pool.

  Returns:
      PaginatedInventoryLogSchemaOut: Paginated list of inventory logs.
  """
  return await InventoryLog.get_logs_by_chemical_raw(pool, id, limit, offset)


@router.post("/{id}/log", response_model=schemas.InventoryLogSchemaOut)
async def create_chemical_log(
  id: int, log: schemas.InventoryLogSchemaIn, db: AsyncSession = Depends(get_db)
):
  """Create a new inventory log entry for a chemical.

  Args:
      id (int): ID of the chemical.
      log (InventoryLogSchemaIn): Log entry data.
      db (AsyncSession): Database session dependency.

  Returns:
      InventoryLogSchemaOut: Created log entry.

  Raises:
      HTTPException: If chemical is not found.
  """
  # Check if chemical exists
  chemical = await db.get(Chemical, id)
  if not chemical:
    raise HTTPException(status_code=404, detail="Chemical not found")

  # Create log
  log_entry = await InventoryLog.create_log(
    db, chemical_id=id, action_type=log.action_type, quantity=log.quantity
  )
  return log_entry
