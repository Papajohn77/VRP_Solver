from typing import Optional
from pydantic import BaseModel

class Customer(BaseModel):
    id: Optional[int]
    name: str
    demand: int
    latitude: float
    longitude: float
    address: str
    model_id: int
    