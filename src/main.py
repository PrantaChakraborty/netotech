from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.chemical import router as chemical_router
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
