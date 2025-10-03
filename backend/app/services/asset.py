from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.asset import Asset
from app.schemas.asset import AssetCreate, AssetUpdate
from app.services.yahoo_finance import fetch_asset_data
from typing import Optional

async def get_assets(db: AsyncSession, skip: int = 0, limit: int = 100):
    """Get all assets with pagination"""
    result = await db.execute(select(Asset).offset(skip).limit(limit))
    return result.scalars().all()

async def get_asset(db: AsyncSession, asset_id: int):
    """Get asset by ID"""
    result = await db.execute(select(Asset).where(Asset.id == asset_id))
    return result.scalar_one_or_none()

async def get_asset_by_ticker(db: AsyncSession, ticker: str):
    """Get asset by ticker"""
    result = await db.execute(select(Asset).where(Asset.ticker == ticker.upper()))
    return result.scalar_one_or_none()

async def create_asset(db: AsyncSession, asset: AssetCreate):
    """Create a new asset"""
    # Check if asset already exists
    existing_asset = await get_asset_by_ticker(db, asset.ticker)
    if existing_asset:
        return existing_asset
    
    db_asset = Asset(**asset.model_dump())
    db.add(db_asset)
    await db.commit()
    await db.refresh(db_asset)
    return db_asset

async def create_asset_from_ticker(db: AsyncSession, ticker: str):
    """Create asset from Yahoo Finance data"""
    # Check if asset already exists
    existing_asset = await get_asset_by_ticker(db, ticker)
    if existing_asset:
        return existing_asset
    
    # Fetch data from Yahoo Finance
    asset_data = await fetch_asset_data(ticker)
    if not asset_data:
        return None
    
    # Create asset
    db_asset = Asset(
        ticker=asset_data.ticker,
        name=asset_data.name,
        exchange=asset_data.exchange,
        currency=asset_data.currency
    )
    
    db.add(db_asset)
    await db.commit()
    await db.refresh(db_asset)
    return db_asset

async def update_asset(db: AsyncSession, asset_id: int, asset: AssetUpdate):
    """Update asset information"""
    db_asset = await get_asset(db, asset_id)
    if not db_asset:
        return None
    
    update_data = asset.model_dump(exclude_unset=True)
    filtered_update_data = {
        k: v for k, v in update_data.items() 
        if v is not None and v != ""
    }
    
    for field, value in filtered_update_data.items():
        setattr(db_asset, field, value)
    
    await db.commit()
    await db.refresh(db_asset)
    return db_asset

async def delete_asset(db: AsyncSession, asset_id: int):
    """Delete an asset"""
    db_asset = await get_asset(db, asset_id)
    if not db_asset:
        return None
    
    await db.delete(db_asset)
    await db.commit()
    return db_asset

async def search_assets_by_ticker(db: AsyncSession, ticker: str):
    """Search assets by ticker (partial match)"""
    result = await db.execute(
        select(Asset).where(Asset.ticker.ilike(f"%{ticker}%"))
    )
    return result.scalars().all()