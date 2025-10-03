import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from decimal import Decimal

from app.models.allocation import Allocation
from app.models.asset import Asset
from app.models.client import Client
from app.schemas.allocation import AllocationCreate, AllocationUpdate
from app.services.allocation import (
    get_allocations, get_allocation, create_allocation, update_allocation,
    delete_allocation, get_client_allocations, get_client_allocation_by_asset
)
from app.database import Base

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
        
        # Create test assets
        asset1 = Asset(ticker="AAPL", name="Apple Inc.", exchange="NASDAQ", currency="USD")
        asset2 = Asset(ticker="GOOGL", name="Alphabet Inc.", exchange="NASDAQ", currency="USD")
        
        session.add_all([client1, client2, asset1, asset2])
        await session.commit()
        await session.refresh(client1)
        await session.refresh(client2)
        await session.refresh(asset1)
        await session.refresh(asset2)
        
        yield session
    
    await engine.dispose()

@pytest.mark.asyncio
async def test_get_allocations(async_session: AsyncSession):
    """Test retrieving all allocations with pagination"""
    # Get test data
    result = await async_session.execute(Client.__table__.select())
    client = result.first()
    result = await async_session.execute(Asset.__table__.select())
    asset = result.first()
    
    # Create test allocations
    for i in range(3):
        allocation = Allocation(
            client_id=client[0],
            asset_id=asset[0],
            quantity=Decimal('10.0'),
            buy_price=Decimal('150.0'),
            buy_date=datetime.utcnow()
        )
        async_session.add(allocation)
    await async_session.commit()
    
    # Test get_allocations with pagination
    allocations = await get_allocations(async_session, skip=1, limit=2)
    
    assert len(allocations) == 2
    assert all(isinstance(alloc, Allocation) for alloc in allocations)

@pytest.mark.asyncio
async def test_get_allocation(async_session: AsyncSession):
    """Test retrieving a specific allocation by ID"""
    # Get test data
    result = await async_session.execute(Client.__table__.select())
    client = result.first()
    result = await async_session.execute(Asset.__table__.select())
    asset = result.first()
    
    # Create test allocation
    allocation = Allocation(
        client_id=client[0],
        asset_id=asset[0],
        quantity=Decimal('100.0'),
        buy_price=Decimal('50.0'),
        buy_date=datetime.utcnow()
    )
    async_session.add(allocation)
    await async_session.commit()
    await async_session.refresh(allocation)
    
    # Test get_allocation
    retrieved_allocation = await get_allocation(async_session, allocation.id)
    
    assert retrieved_allocation is not None
    assert retrieved_allocation.id == allocation.id
    assert retrieved_allocation.quantity == Decimal('100.0')
    assert retrieved_allocation.client_id == client[0]

@pytest.mark.asyncio
async def test_get_allocation_not_found(async_session: AsyncSession):
    """Test retrieving a non-existent allocation"""
    retrieved_allocation = await get_allocation(async_session, 99999)
    assert retrieved_allocation is None

@pytest.mark.asyncio
async def test_create_allocation(async_session: AsyncSession):
    """Test creating a new allocation"""
    # Get test data
    result = await async_session.execute(Client.__table__.select())
    client = result.first()
    result = await async_session.execute(Asset.__table__.select())
    asset = result.first()
    
    allocation_data = AllocationCreate(
        client_id=client[0],
        asset_id=asset[0],
        quantity=Decimal('25.5'),
        buy_price=Decimal('125.75'),
        buy_date=datetime.utcnow()
    )
    
    # Test create_allocation
    created_allocation = await create_allocation(async_session, allocation_data)
    
    assert created_allocation is not None
    assert created_allocation.id is not None
    assert created_allocation.quantity == Decimal('25.5')
    assert created_allocation.buy_price == Decimal('125.75')
    assert created_allocation.client_id == client[0]
    assert created_allocation.asset_id == asset[0]

@pytest.mark.asyncio
async def test_update_allocation(async_session: AsyncSession):
    """Test updating an allocation"""
    # Get test data
    result = await async_session.execute(Client.__table__.select())
    client = result.first()
    result = await async_session.execute(Asset.__table__.select())
    asset = result.first()
    
    # Create test allocation
    allocation = Allocation(
        client_id=client[0],
        asset_id=asset[0],
        quantity=Decimal('50.0'),
        buy_price=Decimal('100.0'),
        buy_date=datetime.utcnow()
    )
    async_session.add(allocation)
    await async_session.commit()
    await async_session.refresh(allocation)
    
    # Test update_allocation
    update_data = AllocationUpdate(
        quantity=Decimal('75.0'),
        buy_price=Decimal('120.0')
    )
    updated_allocation = await update_allocation(async_session, allocation.id, update_data)
    
    assert updated_allocation is not None
    assert updated_allocation.quantity == Decimal('75.0')
    assert updated_allocation.buy_price == Decimal('120.0')
    assert updated_allocation.client_id == client[0]  # Should remain unchanged

@pytest.mark.asyncio
async def test_update_allocation_partial(async_session: AsyncSession):
    """Test partial update of an allocation"""
    # Get test data
    result = await async_session.execute(Client.__table__.select())
    client = result.first()
    result = await async_session.execute(Asset.__table__.select())
    asset = result.first()
    
    # Create test allocation
    allocation = Allocation(
        client_id=client[0],
        asset_id=asset[0],
        quantity=Decimal('50.0'),
        buy_price=Decimal('100.0'),
        buy_date=datetime.utcnow()
    )
    async_session.add(allocation)
    await async_session.commit()
    await async_session.refresh(allocation)
    
    # Test partial update (only quantity)
    update_data = AllocationUpdate(quantity=Decimal('60.0'))
    updated_allocation = await update_allocation(async_session, allocation.id, update_data)
    
    assert updated_allocation is not None
    assert updated_allocation.quantity == Decimal('60.0')
    assert updated_allocation.buy_price == Decimal('100.0')  # Should remain unchanged

@pytest.mark.asyncio
async def test_update_allocation_not_found(async_session: AsyncSession):
    """Test updating a non-existent allocation"""
    update_data = AllocationUpdate(quantity=Decimal('100.0'))
    updated_allocation = await update_allocation(async_session, 99999, update_data)
    assert updated_allocation is None

@pytest.mark.asyncio
async def test_delete_allocation(async_session: AsyncSession):
    """Test deleting an allocation"""
    # Get test data
    result = await async_session.execute(Client.__table__.select())
    client = result.first()
    result = await async_session.execute(Asset.__table__.select())
    asset = result.first()
    
    # Create test allocation
    allocation = Allocation(
        client_id=client[0],
        asset_id=asset[0],
        quantity=Decimal('30.0'),
        buy_price=Decimal('80.0'),
        buy_date=datetime.utcnow()
    )
    async_session.add(allocation)
    await async_session.commit()
    await async_session.refresh(allocation)
    
    # Verify allocation exists
    allocation_before = await get_allocation(async_session, allocation.id)
    assert allocation_before is not None
    
    # Test delete_allocation
    deleted_allocation = await delete_allocation(async_session, allocation.id)
    assert deleted_allocation is not None
    
    # Verify allocation no longer exists
    allocation_after = await get_allocation(async_session, allocation.id)
    assert allocation_after is None

@pytest.mark.asyncio
async def test_delete_allocation_not_found(async_session: AsyncSession):
    """Test deleting a non-existent allocation"""
    deleted_allocation = await delete_allocation(async_session, 99999)
    assert deleted_allocation is None

@pytest.mark.asyncio
async def test_get_client_allocations(async_session: AsyncSession):
    """Test retrieving allocations for a specific client"""
    # Get test data
    result = await async_session.execute(Client.__table__.select())
    clients = result.all()
    client1_id = clients[0][0]
    client2_id = clients[1][0]
    
    result = await async_session.execute(Asset.__table__.select())
    assets = result.all()
    asset1_id = assets[0][0]
    asset2_id = assets[1][0]
    
    # Create allocations for both clients
    allocations_data = [
        (client1_id, asset1_id, Decimal('10.0'), Decimal('150.0')),
        (client1_id, asset2_id, Decimal('5.0'), Decimal('2800.0')),
        (client2_id, asset1_id, Decimal('8.0'), Decimal('155.0')),
    ]
    
    for client_id, asset_id, quantity, buy_price in allocations_data:
        allocation = Allocation(
            client_id=client_id,
            asset_id=asset_id,
            quantity=quantity,
            buy_price=buy_price,
            buy_date=datetime.utcnow()
        )
        async_session.add(allocation)
    await async_session.commit()
    
    # Test get_client_allocations for client1
    client1_allocations = await get_client_allocations(async_session, client1_id)
    
    assert len(client1_allocations) == 2
    assert all(hasattr(alloc, 'asset_ticker') for alloc in client1_allocations)
    assert all(hasattr(alloc, 'asset_name') for alloc in client1_allocations)
    assert all(alloc.client_id == client1_id for alloc in client1_allocations)

@pytest.mark.asyncio
async def test_get_client_allocations_empty(async_session: AsyncSession):
    """Test retrieving allocations for a client with no allocations"""
    # Get test client
    result = await async_session.execute(Client.__table__.select())
    client = result.first()
    client_id = client[0]
    
    # Test get_client_allocations for client with no allocations
    allocations = await get_client_allocations(async_session, client_id)
    
    assert len(allocations) == 0

@pytest.mark.asyncio
async def test_get_client_allocation_by_asset(async_session: AsyncSession):
    """Test retrieving a specific allocation for a client and asset"""
    # Get test data
    result = await async_session.execute(Client.__table__.select())
    clients = result.all()
    client1_id = clients[0][0]
    client2_id = clients[1][0]
    
    result = await async_session.execute(Asset.__table__.select())
    assets = result.all()
    asset1_id = assets[0][0]
    asset2_id = assets[1][0]
    
    # Create allocations
    allocation1 = Allocation(
        client_id=client1_id,
        asset_id=asset1_id,
        quantity=Decimal('20.0'),
        buy_price=Decimal('100.0'),
        buy_date=datetime.utcnow()
    )
    allocation2 = Allocation(
        client_id=client1_id,
        asset_id=asset2_id,
        quantity=Decimal('15.0'),
        buy_price=Decimal('200.0'),
        buy_date=datetime.utcnow()
    )
    async_session.add_all([allocation1, allocation2])
    await async_session.commit()
    await async_session.refresh(allocation1)
    await async_session.refresh(allocation2)
    
    # Test get_client_allocation_by_asset for client1 and asset1
    specific_allocation = await get_client_allocation_by_asset(async_session, client1_id, asset1_id)
    
    assert specific_allocation is not None
    assert specific_allocation.client_id == client1_id
    assert specific_allocation.asset_id == asset1_id
    assert specific_allocation.quantity == Decimal('20.0')

@pytest.mark.asyncio
async def test_get_client_allocation_by_asset_not_found(async_session: AsyncSession):
    """Test retrieving a non-existent client-asset allocation"""
    # Get test data
    result = await async_session.execute(Client.__table__.select())
    client = result.first()
    result = await async_session.execute(Asset.__table__.select())
    asset = result.first()
    
    # Test get_client_allocation_by_asset for non-existent allocation
    allocation = await get_client_allocation_by_asset(async_session, client[0], asset[0])
    assert allocation is None