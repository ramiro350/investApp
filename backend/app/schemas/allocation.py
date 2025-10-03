from pydantic import BaseModel, condecimal
from datetime import datetime
from typing import Optional
from decimal import Decimal

class AllocationBase(BaseModel):
    client_id: int
    asset_id: int
    quantity: condecimal(max_digits=15, decimal_places=6)
    buy_price: condecimal(max_digits=15, decimal_places=2)
    buy_date: datetime

class AllocationCreate(AllocationBase):
    pass

class AllocationUpdate(BaseModel):
    quantity: Optional[condecimal(max_digits=15, decimal_places=6)] = None
    buy_price: Optional[condecimal(max_digits=15, decimal_places=2)] = None
    buy_date: Optional[datetime] = None

class Allocation(AllocationBase):
    id: int

    class Config:
        from_attributes = True

class AllocationWithAsset(Allocation):
    asset_ticker: str
    asset_name: str
    asset_exchange: str
    asset_currency: str
    current_value: Optional[Decimal] = None