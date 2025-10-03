from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.models.allocation import Allocation
from app.models.asset import Asset
from app.schemas.allocation import AllocationCreate, AllocationUpdate
from app.services.asset import get_asset_by_ticker, create_asset_from_ticker, get_asset
from typing import List, Optional

async def get_allocations(db: AsyncSession, skip: int = 0, limit: int = 100):
    """Get all allocations with pagination"""
    result = await db.execute(
        select(Allocation)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()

async def get_allocation(db: AsyncSession, allocation_id: int):
    """Get allocation by ID"""
    result = await db.execute(
        select(Allocation).where(Allocation.id == allocation_id)
    )
    return result.scalar_one_or_none()

async def get_client_allocations(db: AsyncSession, client_id: int):
    """Get all allocations for a specific client"""
    result = await db.execute(
        select(Allocation, Asset)
        .join(Asset, Allocation.asset_id == Asset.id)
        .where(Allocation.client_id == client_id)
    )
    
    allocations_with_assets = []
    for allocation, asset in result:
        allocation_with_asset = allocation
        allocation_with_asset.asset_ticker = asset.ticker
        allocation_with_asset.asset_name = asset.name
        allocation_with_asset.asset_exchange = asset.exchange
        allocation_with_asset.asset_currency = asset.currency
        
        allocations_with_assets.append(allocation_with_asset)
    
    return allocations_with_assets

async def create_allocation(db: AsyncSession, allocation: AllocationCreate):
    """Create a new allocation"""
    # Handle asset creation if ticker is provided
    asset_id = allocation.asset_id
    
    asset = await get_asset(db, asset_id)
    if not asset:
        # Create new asset from ticker
        asset = await create_asset_from_ticker(db, asset_id)
        if not asset:
            return None  # Could not create asset
    
    asset_id = asset.id
    
    if not asset_id:
        return None  # No asset ID or ticker provided
    
    # Create allocation
    db_allocation = Allocation(
        client_id=allocation.client_id,
        asset_id=asset_id,
        quantity=allocation.quantity,
        buy_price=allocation.buy_price,
        buy_date=allocation.buy_date
    )
    
    db.add(db_allocation)
    await db.commit()
    await db.refresh(db_allocation)
    return db_allocation

async def update_allocation(db: AsyncSession, allocation_id: int, allocation: AllocationUpdate):
    """Update allocation information"""
    db_allocation = await get_allocation(db, allocation_id)
    if not db_allocation:
        return None
    
    update_data = allocation.model_dump(exclude_unset=True)
    filtered_update_data = {
        k: v for k, v in update_data.items() 
        if v is not None and v != ""
    }
    
    for field, value in filtered_update_data.items():
        setattr(db_allocation, field, value)
    
    await db.commit()
    await db.refresh(db_allocation)
    return db_allocation

async def delete_allocation(db: AsyncSession, allocation_id: int):
    """Delete an allocation"""
    db_allocation = await get_allocation(db, allocation_id)
    if not db_allocation:
        return None
    
    await db.delete(db_allocation)
    await db.commit()
    return db_allocation

async def get_client_allocation_by_asset(db: AsyncSession, client_id: int, asset_id: int):
    """Get specific allocation for a client and asset"""
    result = await db.execute(
        select(Allocation)
        .where(and_(
            Allocation.client_id == client_id,
            Allocation.asset_id == asset_id
        ))
    )
    return result.scalar_one_or_none()