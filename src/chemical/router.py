from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from src.chemical import schemas
from src.chemical.models import Chemical


from src.database import get_db

router = APIRouter(prefix="/chemicals", tags=["chemical"])

@router.get("/", response_model=list[schemas.ChemicalSchemaOut])
async def get_chemicals(limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),db: AsyncSession = Depends(get_db)):
  chemicals = await Chemical.get_all(db, limit, offset)
  return chemicals

@router.post("/create/", response_model=schemas.ChemicalSchemaOut)
async def create_chemicals(
    chemical: schemas.ChemicalSchemaIn,
    db: AsyncSession = Depends(get_db)):
  chemical = await Chemical.create(db, **chemical.model_dump())
  return chemical

@router.put("/update/{id}/", response_model=schemas.ChemicalSchemaOut)
async def update_chemicals(id: int,
    chemical: schemas.ChemicalSchemaIn,
    db: AsyncSession = Depends(get_db)):
  chemical = await Chemical.update(db, id,  **chemical.model_dump())
  return chemical


@router.delete("/delete/{id}", status_code=status.HTTP_200_OK)
async def delete_chemical(
    id: int, db: AsyncSession = Depends(get_db)):
    return await Chemical.delete(db, id)

@router.get("/{id}/", response_model=schemas.ChemicalSchemaOut)
async def get_chemical_by_id(id: int, db: AsyncSession = Depends(get_db)):
    return await Chemical.get_by_id_raw(db, id)