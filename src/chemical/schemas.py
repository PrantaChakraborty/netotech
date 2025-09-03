from datetime import datetime

from pydantic import BaseModel, PositiveInt

class ChemicalSchemaOut(BaseModel):
  id: int
  name: str
  cas_number: str
  quantity: PositiveInt
  unit: str
  created_at: datetime
  updated_at: datetime

  class Config:
    model_config = {
      "from_attributes": True
    }


class ChemicalSchemaIn(BaseModel):
  name: str
  cas_number: str
  quantity: int
  unit: str

  class Config:
    model_config = {
      "from_attributes": True
    }
