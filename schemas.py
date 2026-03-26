from pydantic import BaseModel
from typing import Optional
from datetime import date

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str

class FuelCreate(BaseModel):
    user_id: int
    odometer: float
    liters: float
    price_per_liter: float
    fill_date: date

class FuelUpdate(BaseModel):
    odometer: Optional[float] = None
    liters: Optional[float] = None
    price_per_liter: Optional[float] = None

class FuelResponse(BaseModel):
    id: int
    user_id: int
    odometer: float
    liters: float
    price_per_liter: float
    total_cost: float
    fill_date: date
    efficiency: Optional[float] = None  # km per liter calculation
