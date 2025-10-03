from pydantic import BaseModel, condecimal
from typing import Optional
from decimal import Decimal

class AssetBase(BaseModel):
    ticker: str
    name: str
    exchange: str
    currency: str

class AssetCreate(AssetBase):
    pass

class AssetUpdate(BaseModel):
    ticker: Optional[str] = None
    name: Optional[str] = None
    exchange: Optional[str] = None
    currency: Optional[str] = None

class Asset(AssetBase):
    id: int

    class Config:
        from_attributes = True

class YahooFinanceResponse(BaseModel):
    ticker: str
    name: str
    exchange: str
    currency: str
    current_price: Optional[Decimal] = None