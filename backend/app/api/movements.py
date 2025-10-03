from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import date, datetime
from app.database import get_db
from app.schemas.movement import (
    Movement, MovementCreate, MovementUpdate, MovementWithClient, 
    MovementSummary, PeriodFilter, OfficeSummary
)
from app.services.movement import (
    get_movements, get_movement, create_movement, update_movement,
    delete_movement, get_client_movements, get_movements_by_period,
    get_movement_summary, get_office_summary, get_client_balance, export_client_movements_csv
)
from app.auth.dependencies import get_current_active_user
from app.models.user import User as UserModel
from fastapi.responses import StreamingResponse
import io

router = APIRouter()

@router.get("/", response_model=list[Movement])
async def read_movements(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """Get all movements with client information"""
    movements = await get_movements(db, skip=skip, limit=limit)
    return movements

@router.post("/", response_model=Movement)
async def create_new_movement(
    movement: MovementCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """Create a new movement (deposit or withdrawal)"""
    return await create_movement(db, movement)

@router.get("/{movement_id}", response_model=Movement)
async def read_movement(
    movement_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """Get a specific movement by ID"""
    db_movement = await get_movement(db, movement_id)
    if db_movement is None:
        raise HTTPException(status_code=404, detail="Movement not found")
    return db_movement

@router.put("/{movement_id}", response_model=Movement)
async def update_existing_movement(
    movement_id: int,
    movement: MovementUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """Update a movement"""
    db_movement = await update_movement(db, movement_id, movement)
    if db_movement is None:
        raise HTTPException(status_code=404, detail="Movement not found")
    return db_movement

@router.delete("/{movement_id}")
async def delete_existing_movement(
    movement_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """Delete a movement"""
    db_movement = await delete_movement(db, movement_id)
    if db_movement is None:
        raise HTTPException(status_code=404, detail="Movement not found")
    return {"message": "Movement deleted successfully"}

@router.get("/client/{client_id}", response_model=list[Movement])
async def read_client_movements(
    client_id: int,
    start_date: Optional[datetime] = Query(None, description="Start date for filtering"),
    end_date: Optional[datetime] = Query(None, description="End date for filtering"),
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """Get all movements for a specific client with optional date range"""
    period_filter = PeriodFilter(
        start_date=start_date,
        end_date=end_date,
        client_id=client_id
    )
    movements = await get_client_movements(db, client_id, period_filter)
    return movements


@router.get("/summary/", response_model=MovementSummary)
async def get_movements_summary(
    start_date: Optional[datetime] = Query(None, description="Start date for filtering"),
    end_date: Optional[datetime] = Query(None, description="End date for filtering"),
    client_id: Optional[int] = Query(None, description="Filter by client ID"),
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """Get summary of movements (deposits, withdrawals, net flow)"""
    period_filter = PeriodFilter(
        start_date=start_date,
        end_date=end_date,
        client_id=client_id
    )
    summary = await get_movement_summary(db, period_filter)
    return summary

@router.get("/office/summary/", response_model=OfficeSummary)
async def get_office_summary_endpoint(
    start_date: Optional[date] = Query(None, description="Start date for filtering"),
    end_date: Optional[date] = Query(None, description="End date for filtering"),
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """Get office-wide summary with breakdown by client"""
    period_filter = PeriodFilter(
        start_date=start_date,
        end_date=end_date
    )
    office_summary = await get_office_summary(db, period_filter)
    return office_summary

@router.get("/client/{client_id}/balance")
async def get_client_current_balance(
    client_id: int,
    as_of_date: Optional[date] = Query(None, description="Get balance as of specific date"),
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """Get client's current balance (total deposits - total withdrawals)"""
    balance = await get_client_balance(db, client_id, as_of_date)
    return {
        "client_id": client_id,
        "balance": balance,
        "as_of_date": as_of_date or datetime.utcnow()
    }


@router.get("/client/{client_id}/export-csv")
async def export_client_movements_csv_endpoint(
    client_id: int,
    start_date: Optional[datetime] = Query(None, description="Start date for filtering"),
    end_date: Optional[datetime] = Query(None, description="End date for filtering"),
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """Export client movements to CSV file"""
    period_filter = PeriodFilter(
        start_date=start_date,
        end_date=end_date,
        client_id=client_id
    )
    
    try:
        csv_file = await export_client_movements_csv(db, client_id, period_filter)
        
        # Create filename with timestamp
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"movements_client_{client_id}_{timestamp}.csv"
        
        return StreamingResponse(
            csv_file,
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Content-Type": "text/csv; charset=utf-8"
            }
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating CSV export: {str(e)}"
        )

