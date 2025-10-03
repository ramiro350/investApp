from sqlalchemy import Column, Integer, ForeignKey, String, Numeric, DateTime, Enum
from sqlalchemy.orm import relationship
from app.database import Base
import enum

class MovementType(enum.Enum):
    deposit = "deposit"
    withdrawal = "withdrawal"

class Movement(Base):
    __tablename__ = "movements"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    type = Column(Enum(MovementType), nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    date = Column(DateTime(timezone=True), nullable=False)
    note = Column(String, nullable=True)

    client = relationship("Client")