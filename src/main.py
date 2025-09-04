from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.chemical import router as chemical_router
from src.database import get_db
from src.exceptions import register_exception_handlers

app = FastAPI()
register_exception_handlers(app)
origins = [
  "http://localhost:8080",
]

app.add_middleware(
  CORSMiddleware,
  allow_origins=["*"],
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

app.include_router(chemical_router.router)


@app.get("/")
async def root():
  return {"message": "Neotech Assignment"}


@app.get(
  "/health",
)
async def health(db: AsyncSession = Depends(get_db)):
  try:
    # Simple DB check
    result = await db.execute(text("SELECT 1"))
    _ = result.scalar()
    return {"status": "ok", "database": "reachable"}
  except Exception as e:
    return {"status": "error", "database": str(e)}
