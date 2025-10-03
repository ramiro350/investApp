from sqlalchemy import Column, Integer, ForeignKey, Numeric, DateTime
from sqlalchemy.orm import relationship
from app.database import Base

class Allocation(Base):
    __tablename__ = "allocations"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)
    quantity = Column(Numeric(15, 6), nullable=False)
    buy_price = Column(Numeric(15, 2), nullable=False)
    buy_date = Column(DateTime(timezone=True), nullable=False)

    client = relationship("Client")
    asset = relationship("Asset")