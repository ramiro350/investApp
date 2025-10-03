from pydantic import BaseModel, condecimal
from datetime import datetime
from typing import Optional
from decimal import Decimal
from enum import Enum

class MovementType(str, Enum):
    deposit = "deposit"
    withdrawal = "withdrawal"

class MovementBase(BaseModel):
    client_id: int
    type: MovementType
    amount: condecimal(max_digits=15, decimal_places=2)
    date: datetime
    note: Optional[str] = None

class MovementCreate(MovementBase):
    pass

class MovementUpdate(BaseModel):
    type: Optional[MovementType] = None
    amount: Optional[condecimal(max_digits=15, decimal_places=2)] = None
    date: Optional[datetime] = None
    note: Optional[str] = None

class Movement(MovementBase):
    id: int

    class Config:
        from_attributes = True

class MovementWithClient(Movement):
    client_name: str
    client_email: str

class MovementSummary(BaseModel):
    total_deposits: Decimal
    total_withdrawals: Decimal
    net_flow: Decimal
    movement_count: int

class PeriodFilter(BaseModel):
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    client_id: Optional[int] = None

class OfficeSummary(BaseModel):
    total_deposits: Decimal
    total_withdrawals: Decimal
    net_flow: Decimal
    total_movements: int
    client_summaries: dict