from typing import Optional
from pydantic import BaseModel

class Vehicle(BaseModel):
    id: Optional[int]
    name: str
    capacity: int
    model_id: int
