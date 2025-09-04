from datetime import datetime

from pydantic import BaseModel, field_serializer

from src.chemical.models import ActionType


class ChemicalSchemaOut(BaseModel):
  id: int
  name: str
  cas_number: str
  quantity: int
  unit: str
  created_at: datetime
  updated_at: datetime

  class Config:
    model_config = {"from_attributes": True}

  @field_serializer("created_at")
  def format_created_at(self, ts: datetime) -> str:
    return ts.strftime("%d %b %Y %I:%M %p")

  @field_serializer("updated_at")
  def format_updated_at(self, ts: datetime) -> str:
    return ts.strftime("%d %b %Y %I:%M %p")


class PaginatedChemicalSchemaOut(BaseModel):
  total: int
  limit: int
  offset: int
  results: list[ChemicalSchemaOut]


class ChemicalSchemaIn(BaseModel):
  name: str
  cas_number: str
  quantity: int
  unit: str

  class Config:
    model_config = {"from_attributes": True}


class InventoryLogSchemaIn(BaseModel):
  action_type: ActionType
  quantity: int

  class Config:
    model_config = {"from_attributes": True}


class InventoryLogSchemaOut(BaseModel):
  id: int
  action_type: str
  quantity: int
  timestamp: datetime
  chemical_id: int

  class Config:
    model_config = {"from_attributes": True}

  @field_serializer("timestamp")
  def format_timestamp(self, ts: datetime) -> str:
    return ts.strftime("%d %b %Y %I:%M %p")


class PaginatedInventoryLogSchemaOut(BaseModel):
  total: int
  limit: int
  offset: int
  results: list[InventoryLogSchemaOut]
