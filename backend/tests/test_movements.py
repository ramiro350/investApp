import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
from decimal import Decimal

from app.models.movement import Movement, MovementType
from app.models.client import Client
from app.schemas.movement import MovementCreate, MovementUpdate, PeriodFilter
from app.services.movement import (
    export_client_movements_csv, get_movements, get_movement, create_movement, update_movement,
    delete_movement, get_client_movements, get_movements_by_period,
    get_movement_summary, get_office_summary, get_client_balance
)
from app.database import Base
import csv
import io

TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

@pytest_asyncio.fixture
async def async_session():
    """Create test database session"""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    async_session_maker = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session_maker() as session:
        # Create test clients
        client1 = Client(name="Client One", email="client1@example.com")
        client2 = Client(name="Client Two", email="client2@example.com")
        session.add_all([client1, client2])
        await session.commit()
        await session.refresh(client1)
        await session.refresh(client2)
        
        yield session
    
    await engine.dispose()

@pytest.mark.asyncio
async def test_create_movement(async_session: AsyncSession):
    """Test creating a new movement"""
    # Get test client
    result = await async_session.execute(Client.__table__.select())
    client = result.first()
    
    movement_data = MovementCreate(
        client_id=client[0],
        type=MovementType.deposit,
        amount=Decimal('1500.50'),
        date=datetime.utcnow(),
        note="Initial deposit"
    )
    
    created_movement = await create_movement(async_session, movement_data)
    
    assert created_movement is not None
    assert created_movement.id is not None
    assert created_movement.type == MovementType.deposit
    assert created_movement.amount == Decimal('1500.50')
    assert created_movement.client_id == client[0]
    assert created_movement.note == "Initial deposit"

@pytest.mark.asyncio
async def test_get_movement(async_session: AsyncSession):
    """Test retrieving a movement by ID"""
    # Get test client and create movement
    result = await async_session.execute(Client.__table__.select())
    client = result.first()
    
    movement_data = MovementCreate(
        client_id=client[0],
        type=MovementType.deposit,
        amount=Decimal('1000.00'),
        date=datetime.utcnow()
    )
    created_movement = await create_movement(async_session, movement_data)
    
    # Retrieve the movement
    retrieved_movement = await get_movement(async_session, created_movement.id)
    
    assert retrieved_movement is not None
    assert retrieved_movement.id == created_movement.id
    assert retrieved_movement.amount == Decimal('1000.00')
    assert retrieved_movement.client_id == client[0]

@pytest.mark.asyncio
async def test_get_movement_not_found(async_session: AsyncSession):
    """Test retrieving a non-existent movement"""
    retrieved_movement = await get_movement(async_session, 99999)
    assert retrieved_movement is None

@pytest.mark.asyncio
async def test_get_movements_with_pagination(async_session: AsyncSession):
    """Test retrieving movements with pagination"""
    # Get test client
    result = await async_session.execute(Client.__table__.select())
    client = result.first()
    
    # Create multiple movements
    for i in range(5):
        movement_data = MovementCreate(
            client_id=client[0],
            type=MovementType.deposit,
            amount=Decimal(f'{1000 + i}.00'),
            date=datetime.utcnow()
        )
        await create_movement(async_session, movement_data)
    
    # Test pagination
    movements = await get_movements(async_session, skip=2, limit=2)
    assert len(movements) == 2

@pytest.mark.asyncio
async def test_update_movement(async_session: AsyncSession):
    """Test updating a movement"""
    # Get test client and create movement
    result = await async_session.execute(Client.__table__.select())
    client = result.first()
    
    movement_data = MovementCreate(
        client_id=client[0],
        type=MovementType.deposit,
        amount=Decimal('500.00'),
        date=datetime.utcnow(),
        note="Original note"
    )
    created_movement = await create_movement(async_session, movement_data)
    
    # Update the movement
    update_data = MovementUpdate(
        amount=Decimal('750.00'),
        note="Updated note"
    )
    updated_movement = await update_movement(async_session, created_movement.id, update_data)
    
    assert updated_movement is not None
    assert updated_movement.amount == Decimal('750.00')
    assert updated_movement.note == "Updated note"
    assert updated_movement.type == MovementType.deposit  # Should remain unchanged

@pytest.mark.asyncio
async def test_update_movement_partial(async_session: AsyncSession):
    """Test partial update of a movement"""
    # Get test client and create movement
    result = await async_session.execute(Client.__table__.select())
    client = result.first()
    
    movement_data = MovementCreate(
        client_id=client[0],
        type=MovementType.deposit,
        amount=Decimal('500.00'),
        date=datetime.utcnow(),
        note="Original note"
    )
    created_movement = await create_movement(async_session, movement_data)
    
    # Update only the amount
    update_data = MovementUpdate(amount=Decimal('600.00'))
    updated_movement = await update_movement(async_session, created_movement.id, update_data)
    
    assert updated_movement is not None
    assert updated_movement.amount == Decimal('600.00')
    assert updated_movement.note == "Original note"  # Should remain unchanged

@pytest.mark.asyncio
async def test_update_movement_not_found(async_session: AsyncSession):
    """Test updating a non-existent movement"""
    update_data = MovementUpdate(amount=Decimal('1000.00'))
    updated_movement = await update_movement(async_session, 99999, update_data)
    assert updated_movement is None

@pytest.mark.asyncio
async def test_delete_movement(async_session: AsyncSession):
    """Test deleting a movement"""
    # Get test client and create movement
    result = await async_session.execute(Client.__table__.select())
    client = result.first()
    
    movement_data = MovementCreate(
        client_id=client[0],
        type=MovementType.deposit,
        amount=Decimal('1000.00'),
        date=datetime.utcnow()
    )
    created_movement = await create_movement(async_session, movement_data)
    
    # Verify movement exists
    movement_before = await get_movement(async_session, created_movement.id)
    assert movement_before is not None
    
    # Delete movement
    deleted_movement = await delete_movement(async_session, created_movement.id)
    assert deleted_movement is not None
    
    # Verify movement no longer exists
    movement_after = await get_movement(async_session, created_movement.id)
    assert movement_after is None

@pytest.mark.asyncio
async def test_delete_movement_not_found(async_session: AsyncSession):
    """Test deleting a non-existent movement"""
    deleted_movement = await delete_movement(async_session, 99999)
    assert deleted_movement is None

@pytest.mark.asyncio
async def test_get_client_movements(async_session: AsyncSession):
    """Test retrieving movements for a specific client"""
    # Get test clients
    result = await async_session.execute(Client.__table__.select())
    clients = result.all()
    client1_id = clients[0][0]
    client2_id = clients[1][0]
    
    # Create movements for both clients
    for client_id in [client1_id, client1_id, client2_id]:
        movement_data = MovementCreate(
            client_id=client_id,
            type=MovementType.deposit,
            amount=Decimal('500.00'),
            date=datetime.utcnow()
        )
        await create_movement(async_session, movement_data)
    
    # Get movements for client1 only
    client1_movements = await get_client_movements(async_session, client1_id)
    assert len(client1_movements) == 2
    assert all(m.client_id == client1_id for m in client1_movements)

@pytest.mark.asyncio
async def test_get_client_movements_with_period_filter(async_session: AsyncSession):
    """Test retrieving client movements with date filter"""
    # Get test client
    result = await async_session.execute(Client.__table__.select())
    client = result.first()
    client_id = client[0]
    
    now = datetime.utcnow()
    yesterday = now - timedelta(days=1)
    tomorrow = now + timedelta(days=1)
    
    # Create movements with different dates
    movement1 = MovementCreate(
        client_id=client_id,
        type=MovementType.deposit,
        amount=Decimal('1000.00'),
        date=yesterday
    )
    movement2 = MovementCreate(
        client_id=client_id,
        type=MovementType.deposit,
        amount=Decimal('500.00'),
        date=tomorrow
    )
    
    await create_movement(async_session, movement1)
    await create_movement(async_session, movement2)
    
    # Filter by period (only yesterday)
    period_filter = PeriodFilter(
        start_date=yesterday,
        end_date=now
    )
    movements = await get_client_movements(async_session, client_id, period_filter)
    
    assert len(movements) == 1
    assert movements[0].amount == Decimal('1000.00')

@pytest.mark.asyncio
async def test_get_movements_by_period(async_session: AsyncSession):
    """Test retrieving movements filtered by period"""
    # Get test clients
    result = await async_session.execute(Client.__table__.select())
    clients = result.all()
    client1_id = clients[0][0]
    client2_id = clients[1][0]
    
    now = datetime.utcnow()
    last_week = now - timedelta(days=7)
    next_week = now + timedelta(days=7)
    
    # Create movements with different dates
    movements_data = [
        MovementCreate(client_id=client1_id, type=MovementType.deposit, amount=Decimal('1000.00'), date=last_week),
        MovementCreate(client_id=client2_id, type=MovementType.withdrawal, amount=Decimal('500.00'), date=now),
        MovementCreate(client_id=client1_id, type=MovementType.deposit, amount=Decimal('750.00'), date=next_week),
    ]
    
    for movement_data in movements_data:
        await create_movement(async_session, movement_data)
    
    # Filter by period (last week to now)
    period_filter = PeriodFilter(
        start_date=last_week,
        end_date=now
    )
    movements = await get_movements_by_period(async_session, period_filter)
    
    assert len(movements) == 2  # Only movements from last_week to now

@pytest.mark.asyncio
async def test_get_movements_by_period_with_client_filter(async_session: AsyncSession):
    """Test retrieving movements filtered by period and client"""
    # Get test clients
    result = await async_session.execute(Client.__table__.select())
    clients = result.all()
    client1_id = clients[0][0]
    client2_id = clients[1][0]
    
    # Create movements for both clients
    for client_id in [client1_id, client1_id, client2_id]:
        movement_data = MovementCreate(
            client_id=client_id,
            type=MovementType.deposit,
            amount=Decimal('500.00'),
            date=datetime.utcnow()
        )
        await create_movement(async_session, movement_data)
    
    # Filter by client1 only
    period_filter = PeriodFilter(client_id=client1_id)
    movements = await get_movements_by_period(async_session, period_filter)
    
    assert len(movements) == 2
    assert all(m.client_id == client1_id for m in movements)

@pytest.mark.asyncio
async def test_get_movement_summary(async_session: AsyncSession):
    """Test movement summary calculation"""
    # Get test client
    result = await async_session.execute(Client.__table__.select())
    client = result.first()
    client_id = client[0]
    
    # Create test movements
    movements_data = [
        MovementCreate(client_id=client_id, type=MovementType.deposit, amount=Decimal('2000.00'), date=datetime.utcnow()),
        MovementCreate(client_id=client_id, type=MovementType.deposit, amount=Decimal('1000.00'), date=datetime.utcnow()),
        MovementCreate(client_id=client_id, type=MovementType.withdrawal, amount=Decimal('500.00'), date=datetime.utcnow()),
        MovementCreate(client_id=client_id, type=MovementType.withdrawal, amount=Decimal('300.00'), date=datetime.utcnow()),
    ]
    
    for movement_data in movements_data:
        await create_movement(async_session, movement_data)
    
    # Get summary
    summary = await get_movement_summary(async_session, PeriodFilter(client_id=client_id))
    
    assert summary.total_deposits == Decimal('3000.00')
    assert summary.total_withdrawals == Decimal('800.00')
    assert summary.net_flow == Decimal('2200.00')
    assert summary.movement_count == 4

@pytest.mark.asyncio
async def test_get_movement_summary_empty(async_session: AsyncSession):
    """Test movement summary with no movements"""
    summary = await get_movement_summary(async_session)
    
    assert summary.total_deposits == Decimal('0')
    assert summary.total_withdrawals == Decimal('0')
    assert summary.net_flow == Decimal('0')
    assert summary.movement_count == 0

@pytest.mark.asyncio
async def test_get_office_summary(async_session: AsyncSession):
    """Test office-wide summary with client breakdown"""
    # Get test clients
    result = await async_session.execute(Client.__table__.select())
    clients = result.all()
    client1_id = clients[0][0]
    client2_id = clients[1][0]
    
    # Create movements for both clients
    movements_data = [
        MovementCreate(client_id=client1_id, type=MovementType.deposit, amount=Decimal('2000.00'), date=datetime.utcnow()),
        MovementCreate(client_id=client1_id, type=MovementType.withdrawal, amount=Decimal('500.00'), date=datetime.utcnow()),
        MovementCreate(client_id=client2_id, type=MovementType.deposit, amount=Decimal('1000.00'), date=datetime.utcnow()),
        MovementCreate(client_id=client2_id, type=MovementType.withdrawal, amount=Decimal('200.00'), date=datetime.utcnow()),
    ]
    
    for movement_data in movements_data:
        await create_movement(async_session, movement_data)
    
    # Get office summary
    office_summary = await get_office_summary(async_session)
    
    # Check overall totals
    assert office_summary.total_deposits == Decimal('3000.00')
    assert office_summary.total_withdrawals == Decimal('700.00')
    assert office_summary.net_flow == Decimal('2300.00')
    assert office_summary.total_movements == 4
    
    # Check client breakdowns
    assert client1_id in office_summary.client_summaries
    assert client2_id in office_summary.client_summaries
    
    client1_summary = office_summary.client_summaries[client1_id]['summary']
    assert client1_summary.total_deposits == Decimal('2000.00')
    assert client1_summary.total_withdrawals == Decimal('500.00')

@pytest.mark.asyncio
async def test_get_client_balance(async_session: AsyncSession):
    """Test client balance calculation"""
    # Get test client
    result = await async_session.execute(Client.__table__.select())
    client = result.first()
    client_id = client[0]
    
    # Create test movements
    movements_data = [
        MovementCreate(client_id=client_id, type=MovementType.deposit, amount=Decimal('3000.00'), date=datetime.utcnow()),
        MovementCreate(client_id=client_id, type=MovementType.withdrawal, amount=Decimal('1000.00'), date=datetime.utcnow()),
        MovementCreate(client_id=client_id, type=MovementType.withdrawal, amount=Decimal('500.00'), date=datetime.utcnow()),
    ]
    
    for movement_data in movements_data:
        await create_movement(async_session, movement_data)
    
    # Get balance
    balance = await get_client_balance(async_session, client_id)
    
    assert balance == Decimal('1500.00')  # 3000 - 1000 - 500

@pytest.mark.asyncio
async def test_get_client_balance_with_date_filter(async_session: AsyncSession):
    """Test client balance calculation with date filter"""
    # Get test client
    result = await async_session.execute(Client.__table__.select())
    client = result.first()
    client_id = client[0]
    
    now = datetime.utcnow()
    yesterday = now - timedelta(days=1)
    tomorrow = now + timedelta(days=1)
    
    # Create movements with different dates
    movements_data = [
        MovementCreate(client_id=client_id, type=MovementType.deposit, amount=Decimal('2000.00'), date=yesterday),
        MovementCreate(client_id=client_id, type=MovementType.withdrawal, amount=Decimal('500.00'), date=now),
        MovementCreate(client_id=client_id, type=MovementType.deposit, amount=Decimal('1000.00'), date=tomorrow),
    ]
    
    for movement_data in movements_data:
        await create_movement(async_session, movement_data)
    
    # Get balance as of now (should exclude tomorrow's deposit)
    balance = await get_client_balance(async_session, client_id, now)
    
    assert balance == Decimal('1500.00')  # 2000 - 500 (excludes tomorrow's 1000)

@pytest.mark.asyncio
async def test_get_client_balance_empty(async_session: AsyncSession):
    """Test client balance with no movements"""
    # Get test client
    result = await async_session.execute(Client.__table__.select())
    client = result.first()
    client_id = client[0]
    
    balance = await get_client_balance(async_session, client_id)
    assert balance == Decimal('0')

@pytest.mark.asyncio
async def test_export_client_movements_csv_basic(async_session: AsyncSession):
    """Test basic CSV export of client movements"""
    # Get test client
    result = await async_session.execute(Client.__table__.select())
    client = result.first()
    client_id = client[0]
    
    # Create test movements
    movements_data = [
        Movement(client_id=client_id, type=MovementType.deposit, amount=Decimal('1000.00'), date=datetime.utcnow(), note="Initial deposit"),
        Movement(client_id=client_id, type=MovementType.withdrawal, amount=Decimal('200.00'), date=datetime.utcnow(), note="Withdrawal for expenses"),
    ]
    
    for movement in movements_data:
        async_session.add(movement)
    await async_session.commit()
    
    # Test CSV export
    csv_output = await export_client_movements_csv(async_session, client_id)
    
    # Verify CSV content
    csv_content = csv_output.getvalue()
    lines = csv_content.strip().split('\n')
    
    # Check header
    assert 'ID,Date,Type,Amount,Currency,Note' in lines[0]
    
    # Check data rows (skip header)
    data_rows = lines[1:]
    assert len(data_rows) == 2
    
    # Parse CSV rows
    reader = csv.reader(io.StringIO(csv_content))
    rows = list(reader)
    
    # Verify header
    expected_header = ['ID', 'Date', 'Type', 'Amount', 'Currency', 'Note', 'Client Name', 'Client Email', 'Created At']
    assert rows[0] == expected_header
    
    # Verify data
    assert len(rows) == 3  # header + 2 data rows
    assert rows[1][3] == '200.0'   # Amount of first movement