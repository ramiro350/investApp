from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.database import get_db
from app.schemas.asset import Asset, AssetCreate, AssetUpdate
from app.services.asset import (
    get_assets, get_asset, create_asset, update_asset, delete_asset,
    search_assets_by_ticker, create_asset_from_ticker
)
from app.services.yahoo_finance import fetch_asset_data
from app.auth.dependencies import get_current_active_user
from app.models.user import User as UserModel

router = APIRouter()

@router.get("/", response_model=list[Asset])
async def read_assets(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """Get all assets with pagination"""
    assets = await get_assets(db, skip=skip, limit=limit)
    return assets

@router.post("/", response_model=Asset)
async def create_new_asset(
    asset: AssetCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """Create a new asset"""
    return await create_asset(db, asset)

@router.post("/from-ticker/{ticker}", response_model=Asset)
async def create_asset_from_ticker_endpoint(
    ticker: str,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """Create asset from Yahoo Finance ticker"""
    asset = await create_asset_from_ticker(db, ticker)
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Could not fetch data for ticker {ticker}"
        )
    return asset

@router.get("/{asset_id}", response_model=Asset)
async def read_asset(
    asset_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """Get a specific asset by ID"""
    db_asset = await get_asset(db, asset_id)
    if db_asset is None:
        raise HTTPException(status_code=404, detail="Asset not found")
    return db_asset

@router.put("/{asset_id}", response_model=Asset)
async def update_existing_asset(
    asset_id: int,
    asset: AssetUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """Update an asset"""
    db_asset = await update_asset(db, asset_id, asset)
    if db_asset is None:
        raise HTTPException(status_code=404, detail="Asset not found")
    return db_asset

@router.delete("/{asset_id}")
async def delete_existing_asset(
    asset_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """Delete an asset"""
    db_asset = await delete_asset(db, asset_id)
    if db_asset is None:
        raise HTTPException(status_code=404, detail="Asset not found")
    return {"message": "Asset deleted successfully"}

@router.get("/search/{ticker}", response_model=list[Asset])
async def search_assets(
    ticker: str,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """Search assets by ticker"""
    assets = await search_assets_by_ticker(db, ticker)
    return assets

@router.get("/fetch-yahoo/{ticker}")
async def fetch_yahoo_data(
    ticker: str,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """Fetch data from Yahoo Finance for a ticker"""
    asset_data = await fetch_asset_data(ticker)
    if not asset_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Could not fetch data for ticker {ticker}"
        )
    return asset_data