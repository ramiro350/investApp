from sqlalchemy.orm import Session
from app.models.client import Client
from app.schemas.client import ClientCreate, ClientUpdate, ClientSearch
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

async def get_clients(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(Client).offset(skip).limit(limit))
    return result.scalars().all()

async def create_client(db: AsyncSession, client: ClientCreate):
    db_client = Client(**client.model_dump())
    db.add(db_client)
    await db.commit()
    await db.refresh(db_client)
    return db_client

async def get_client(db: Session, client_id: int):
    result = await db.execute(select(Client).where(Client.id == client_id))
    return result.scalar_one_or_none()

async def update_client(db: Session, client_id: int, client: ClientUpdate):
    db_client = await get_client(db, client_id)
    if db_client:
        update_data = client.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_client, field, value)
        await db.commit()
        await db.refresh(db_client)
    return db_client

async def delete_client(db: Session, client_id: int):
    db_client = await get_client(db, client_id)
    if db_client:
        await db.delete(db_client)
        await db.commit()
    return db_client

async def search_clients(db: AsyncSession, search: ClientSearch):
    """Search clients with filters and pagination"""
    query = select(Client)
    
    # Apply filters
    if search.name:
        query = query.where(Client.name.ilike(f"%{search.name}%"))
    
    if search.email:
        query = query.where(Client.email.ilike(f"%{search.email}%"))
    
    if search.is_active is not None:
        query = query.where(Client.is_active == search.is_active)
    
    # Apply pagination
    query = query.offset(search.skip).limit(search.limit)
    
    result = await db.execute(query)
    return result.scalars().all()

async def get_clients_count(db: AsyncSession, is_active: Optional[bool] = None):
    """Get total count of clients, optionally filtered by status"""
    query = select(Client)
    
    if is_active is not None:
        query = query.where(Client.is_active == is_active)
    
    result = await db.execute(query)
    return len(result.scalars().all())