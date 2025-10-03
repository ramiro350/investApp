import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker as sync_sessionmaker
from app.models.client import Client
from app.schemas.client import ClientCreate, ClientSearch, ClientUpdate
from app.services.client import get_clients, create_client, get_client, get_clients_count, search_clients, update_client, delete_client
from app.database import Base

# Test database URLs
TEST_ASYNC_DB_URL = "sqlite+aiosqlite:///./test_async.db"
TEST_SYNC_DB_URL = "sqlite:///./test_sync.db"

@pytest_asyncio.fixture
async def async_session():
    """Create async test database session"""
    engine = create_async_engine(TEST_ASYNC_DB_URL, echo=False)
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    async_session_maker = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session_maker() as session:
        yield session
    
    await engine.dispose()

@pytest.fixture
def sync_session():
    """Create sync test database session"""
    engine = create_engine(TEST_SYNC_DB_URL, echo=False)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    
    Session = sync_sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = Session()
    
    try:
        yield session
    finally:
        session.close()
        engine.dispose()

@pytest.mark.asyncio
async def test_create_client(async_session: AsyncSession):
    """Test creating a new client - ONE TEST FOR CREATE METHOD"""
    # Arrange
    client_data = ClientCreate(
        name="Test Client",
        email="test@example.com",
        is_active=True
    )
    
    # Act
    created_client = await create_client(async_session, client_data)
    
    # Assert
    assert created_client.id is not None
    assert created_client.name == "Test Client"
    assert created_client.email == "test@example.com"
    assert created_client.is_active == True

@pytest.mark.asyncio
async def test_get_client(async_session: AsyncSession):
    """Test retrieving a client by ID"""
    client_data = ClientCreate(name="Test Client", email="test@example.com")
    created_client = await create_client(async_session, client_data)
    
    retrieved_client = await get_client(async_session, created_client.id)
    
    assert retrieved_client is not None
    assert retrieved_client.id == created_client.id
    assert retrieved_client.name == "Test Client"

@pytest.mark.asyncio
async def test_get_clients_with_pagination(async_session: AsyncSession):
    """Test retrieving clients with pagination"""
    # Create multiple clients
    for i in range(5):
        client_data = ClientCreate(name=f"Client {i}", email=f"client{i}@example.com")
        await create_client(async_session, client_data)
    
    # Test pagination
    clients = await get_clients(async_session, skip=2, limit=2)
    assert len(clients) == 2

@pytest.mark.asyncio
async def test_update_client(async_session: AsyncSession):
    """Test updating a client"""
    client_data = ClientCreate(name="Original Name", email="original@example.com")
    created_client = await create_client(async_session, client_data)
    
    update_data = ClientUpdate(name="Updated Name", email="updated@example.com")
    updated_client = await update_client(async_session, created_client.id, update_data)
    
    assert updated_client is not None
    assert updated_client.name == "Updated Name"
    assert updated_client.email == "updated@example.com"

@pytest.mark.asyncio
async def test_delete_client(async_session: AsyncSession):
    """Test deleting a client"""
    client_data = ClientCreate(name="To Delete", email="delete@example.com")
    created_client = await create_client(async_session, client_data)
    
    # Verify client exists
    client_before = await get_client(async_session, created_client.id)
    assert client_before is not None
    
    # Delete client
    deleted_client = await delete_client(async_session, created_client.id)
    assert deleted_client is not None
    
    # Verify client was deleted
    client_after = await get_client(async_session, created_client.id)
    assert client_after is None

@pytest.mark.asyncio
async def test_search_clients_by_name(async_session: AsyncSession):
    """Test searching clients by name"""
    # Create test clients
    clients_data = [
        ClientCreate(name="John Doe", email="john@example.com"),
        ClientCreate(name="Jane Smith", email="jane@example.com"),
        ClientCreate(name="Bob Johnson", email="bob@example.com"),
    ]
    
    for client_data in clients_data:
        await create_client(async_session, client_data)
    
    # Search for "John"
    search_params = ClientSearch(name="John", skip=0, limit=10)
    results = await search_clients(async_session, search_params)
    
    assert len(results) == 2  # John Doe and Bob Johnson
    assert any(client.name == "John Doe" for client in results)
    assert any(client.name == "Bob Johnson" for client in results)

@pytest.mark.asyncio
async def test_get_clients_count(async_session: AsyncSession):
    """Test getting clients count"""
    # Create mixed active/inactive clients
    clients_data = [
        ClientCreate(name="Client 1", email="c1@example.com", is_active=True),
        ClientCreate(name="Client 2", email="c2@example.com", is_active=True),
        ClientCreate(name="Client 3", email="c3@example.com", is_active=False),
    ]
    
    for client_data in clients_data:
        await create_client(async_session, client_data)
    
    # Test total count
    total_count = await get_clients_count(async_session)
    assert total_count == 3
    
    # Test active count
    active_count = await get_clients_count(async_session, is_active=True)
    assert active_count == 2
    
    # Test inactive count
    inactive_count = await get_clients_count(async_session, is_active=False)
    assert inactive_count == 1