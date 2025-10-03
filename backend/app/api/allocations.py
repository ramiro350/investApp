from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.database import get_db
from app.schemas.allocation import Allocation, AllocationCreate, AllocationUpdate, AllocationWithAsset
from app.services.allocation import (
    get_allocations, get_allocation, create_allocation, update_allocation,
    delete_allocation, get_client_allocations
)
from app.auth.dependencies import get_current_active_user
from app.models.user import User as UserModel

router = APIRouter()

@router.get("/", response_model=list[Allocation])
async def read_allocations(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """Get all allocations with pagination"""
    allocations = await get_allocations(db, skip=skip, limit=limit)
    return allocations

@router.post("/", response_model=Allocation)
async def create_new_allocation(
    allocation: AllocationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """Create a new allocation"""
    db_allocation = await create_allocation(db, allocation)
    if not db_allocation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not create allocation. Check if asset exists."
        )
    return db_allocation

@router.get("/{allocation_id}", response_model=Allocation)
async def read_allocation(
    allocation_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """Get a specific allocation by ID"""
    db_allocation = await get_allocation(db, allocation_id)
    if db_allocation is None:
        raise HTTPException(status_code=404, detail="Allocation not found")
    return db_allocation

@router.get("/client/{client_id}", response_model=list[AllocationWithAsset])
async def read_client_allocations(
    client_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """Get all allocations for a specific client"""
    allocations = await get_client_allocations(db, client_id)
    return allocations

@router.put("/{allocation_id}", response_model=Allocation)
async def update_existing_allocation(
    allocation_id: int,
    allocation: AllocationUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """Update an allocation"""
    db_allocation = await update_allocation(db, allocation_id, allocation)
    if db_allocation is None:
        raise HTTPException(status_code=404, detail="Allocation not found")
    return db_allocation

@router.delete("/{allocation_id}")
async def delete_existing_allocation(
    allocation_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """Delete an allocation"""
    db_allocation = await delete_allocation(db, allocation_id)
    if db_allocation is None:
        raise HTTPException(status_code=404, detail="Allocation not found")
    return {"message": "Allocation deleted successfully"}