from typing import Optional
from pydantic import BaseModel

class Depot(BaseModel):
    id: Optional[int]
    name: str
    latitude: float
    longitude: float
    address: str
    model_id: int
