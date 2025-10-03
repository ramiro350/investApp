from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import joinedload
from app.models.movement import Movement, MovementType
from app.models.client import Client
from app.schemas.movement import MovementCreate, MovementUpdate, MovementSummary, PeriodFilter, OfficeSummary
from typing import List, Optional
from decimal import Decimal
from datetime import datetime
import csv
import io

async def get_movements(db: AsyncSession, skip: int = 0, limit: int = 100):
    """Get all movements with pagination"""
    result = await db.execute(
        select(Movement)
        .options(joinedload(Movement.client))
        .offset(skip)
        .limit(limit)
        .order_by(Movement.date.desc())
    )
    return result.scalars().all()

async def get_movement(db: AsyncSession, movement_id: int):
    """Get movement by ID"""
    result = await db.execute(
        select(Movement)
        .options(joinedload(Movement.client))
        .where(Movement.id == movement_id)
    )
    return result.scalar_one_or_none()

async def create_movement(db: AsyncSession, movement: MovementCreate):
    """Create a new movement"""
    db_movement = Movement(**movement.model_dump())
    db.add(db_movement)
    await db.commit()
    await db.refresh(db_movement)

    return db_movement

async def update_movement(db: AsyncSession, movement_id: int, movement: MovementUpdate):
    """Update movement information"""
    db_movement = await get_movement(db, movement_id)
    if not db_movement:
        return None
    
    update_data = movement.model_dump(exclude_unset=True)
    filtered_update_data = {
        k: v for k, v in update_data.items() 
        if v is not None and v != ""
    }
    
    for field, value in filtered_update_data.items():
        setattr(db_movement, field, value)
    
    await db.commit()
    await db.refresh(db_movement)
    return db_movement

async def delete_movement(db: AsyncSession, movement_id: int):
    """Delete a movement"""
    db_movement = await get_movement(db, movement_id)
    if not db_movement:
        return None
    
    await db.delete(db_movement)
    await db.commit()
    return db_movement

async def get_client_movements(db: AsyncSession, client_id: int, period_filter: Optional[PeriodFilter] = None):
    """Get all movements for a specific client with optional period filter"""
    query = select(Movement).where(Movement.client_id == client_id)
    
    if period_filter:
        if period_filter.start_date:
            query = query.where(Movement.date >= period_filter.start_date)
        if period_filter.end_date:
            query = query.where(Movement.date <= period_filter.end_date)
    
    query = query.order_by(Movement.date.desc())
    result = await db.execute(query)
    return result.scalars().all()

async def get_movements_by_period(db: AsyncSession, period_filter: PeriodFilter):
    """Get movements filtered by period and optionally by client"""
    query = select(Movement).options(joinedload(Movement.client))
    
    # Apply date filters
    if period_filter.start_date:
        query = query.where(Movement.date >= period_filter.start_date)
    if period_filter.end_date:
        query = query.where(Movement.date <= period_filter.end_date)
    
    # Apply client filter if provided
    if period_filter.client_id:
        query = query.where(Movement.client_id == period_filter.client_id)
    
    query = query.order_by(Movement.date.desc())
    result = await db.execute(query)
    return result.scalars().all()

async def get_movement_summary(db: AsyncSession, period_filter: Optional[PeriodFilter] = None) -> MovementSummary:
    """Get summary of movements (deposits, withdrawals, net flow)"""
    query = select(Movement)
    
    # Apply filters if provided
    if period_filter:
        if period_filter.start_date:
            query = query.where(Movement.date >= period_filter.start_date)
        if period_filter.end_date:
            query = query.where(Movement.date <= period_filter.end_date)
        if period_filter.client_id:
            query = query.where(Movement.client_id == period_filter.client_id)
    
    # Get all movements matching the filter
    result = await db.execute(query)
    movements = result.scalars().all()
    
    # Calculate totals
    total_deposits = Decimal('0')
    total_withdrawals = Decimal('0')
    
    for movement in movements:
        if movement.type == MovementType.deposit:
            total_deposits += movement.amount
        else:
            total_withdrawals += movement.amount
    
    net_flow = total_deposits - total_withdrawals
    
    return MovementSummary(
        total_deposits=total_deposits,
        total_withdrawals=total_withdrawals,
        net_flow=net_flow,
        movement_count=len(movements)
    )

async def get_office_summary(db: AsyncSession, period_filter: Optional[PeriodFilter] = None) -> OfficeSummary:
    """Get office-wide summary with breakdown by client"""
    # Get overall summary
    overall_summary = await get_movement_summary(db, period_filter)
    
    # Get all clients
    clients_result = await db.execute(select(Client))
    clients = clients_result.scalars().all()
    
    # Get summary for each client
    client_summaries = {}
    for client in clients:
        client_filter = PeriodFilter(
            start_date=period_filter.start_date if period_filter else None,
            end_date=period_filter.end_date if period_filter else None,
            client_id=client.id
        )
        client_summary = await get_movement_summary(db, client_filter)
        client_summaries[client.id] = {
            "client_name": client.name,
            "client_email": client.email,
            "summary": client_summary
        }
    
    return OfficeSummary(
        total_deposits=overall_summary.total_deposits,
        total_withdrawals=overall_summary.total_withdrawals,
        net_flow=overall_summary.net_flow,
        total_movements=overall_summary.movement_count,
        client_summaries=client_summaries
    )

async def get_client_balance(db: AsyncSession, client_id: int, as_of_date: Optional[datetime] = None) -> Decimal:
    """Get client's current balance (total deposits - total withdrawals)"""
    query = select(Movement).where(Movement.client_id == client_id)
    
    if as_of_date:
        query = query.where(Movement.date <= as_of_date)
    
    result = await db.execute(query)
    movements = result.scalars().all()
    
    balance = Decimal('0')
    for movement in movements:
        if movement.type == MovementType.deposit:
            balance += movement.amount
        else:
            balance -= movement.amount
    
    return balance

async def export_client_movements_csv(db: AsyncSession, client_id: int, period_filter: Optional[PeriodFilter] = None) -> io.StringIO:
    """Export client movements to CSV format"""
    # Use async query with proper relationship loading
    query = select(Movement).options(joinedload(Movement.client)).where(Movement.client_id == client_id)
    
    if period_filter:
        if period_filter.start_date:
            query = query.where(Movement.date >= period_filter.start_date)
        if period_filter.end_date:
            query = query.where(Movement.date <= period_filter.end_date)
    
    query = query.order_by(Movement.date.desc())
    result = await db.execute(query)
    movements = result.scalars().all()
    
    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        'ID', 'Date', 'Type', 'Amount', 'Currency', 'Note',
        'Client Name', 'Client Email', 'Created At'
    ])
    
    # Write data rows
    for movement in movements:
        writer.writerow([
            movement.id,
            movement.date.strftime('%Y-%m-%d %H:%M:%S'),
            movement.type.value,
            float(movement.amount),
            'BRL',  # You might want to make this dynamic based on your data
            movement.note or '',
            movement.client.name if movement.client else '',
            movement.client.email if movement.client else '',
            movement.date.strftime('%Y-%m-%d %H:%M:%S')
        ])
    
    output.seek(0)
    return output