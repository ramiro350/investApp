from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.user import User, UserCreate, UserLogin, Token
from app.services.user import create_user, authenticate_user
from app.auth.jwt import create_access_token
from app.auth.dependencies import get_current_active_user
from app.schemas.client import Client, ClientCreate, ClientUpdate, ClientSearch
from app.services import client as crud_services
from app.models.user import User as UserModel
from typing import Optional

router = APIRouter()

@router.get("/", response_model=list[Client])
async def get_clients(
    skip: int = 0, 
    limit: int = 100, 
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    clients = await crud_services.get_clients(db, skip=skip, limit=limit)
    return clients

@router.post("/", response_model=ClientCreate)
async def create_client(
    client: ClientCreate, 
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    return await crud_services.create_client(db=db, client=client)

@router.get("/{client_id}", response_model=Client)
async def read_client(
    client_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """Get a specific client by ID"""
    db_client = await crud_services.get_client(db, client_id)
    if db_client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    return db_client

@router.put("/{client_id}", response_model=Client)
async def update_existing_client(
    client_id: int,
    client: ClientUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """Update a client"""
    db_client = await crud_services.update_client(db, client_id, client)
    if db_client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    return db_client

@router.delete("/{client_id}")
async def delete_existing_client(
    client_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """Delete a client"""
    db_client = await crud_services.delete_client(db, client_id)
    if db_client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    return {"message": "Client deleted successfully"}

@router.get("/search/", response_model=list[Client])
async def search_clients_endpoint(
    name: Optional[str] = Query(None, description="Search by name (partial match)"),
    email: Optional[str] = Query(None, description="Search by email (partial match)"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """Search clients with filters"""
    search_params = ClientSearch(
        name=name,
        email=email,
        is_active=is_active,
        skip=skip,
        limit=limit
    )
    clients = await crud_services.search_clients(db, search_params)
    return clients

@router.get("/stats/count")
async def get_clients_stats(
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """Get clients count statistics"""
    count = await crud_services.get_clients_count(db, is_active)
    return {"count": count, "is_active": is_active}