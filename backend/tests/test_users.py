import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# Import your app modules
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.services.user import delete_user, get_user_by_email, create_user, authenticate_user, get_user_by_id, get_users, update_user
from app.database import Base
from app.auth.jwt import verify_password

# Test database URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

@pytest_asyncio.fixture
async def async_session():
    """Create test database session"""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    
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

@pytest.mark.asyncio
async def test_create_user(async_session: AsyncSession):
    """Test creating a new user with hashed password - ONE TEST FOR CREATE METHOD"""
    # Arrange
    user_data = UserCreate(
        email="test@example.com",
        password="plainpassword",
        is_active=True
    )
    
    # Act
    created_user = await create_user(async_session, user_data)
    
    # Assert
    assert created_user.id is not None
    assert created_user.email == "test@example.com"
    assert created_user.is_active == True
    # Password should be hashed, not stored in plain text
    assert created_user.password != "plainpassword"
    assert verify_password("plainpassword", created_user.password)

@pytest.mark.asyncio
async def test_get_user_by_email(async_session: AsyncSession):
    """Test retrieving a user by email"""
    # Arrange
    user_data = UserCreate(
        email="test@example.com",
        password="password123",
        is_active=True
    )
    await create_user(async_session, user_data)
    
    # Act
    retrieved_user = await get_user_by_email(async_session, "test@example.com")
    
    # Assert
    assert retrieved_user is not None
    assert retrieved_user.email == "test@example.com"
    assert verify_password("password123", retrieved_user.password)


@pytest.mark.asyncio
async def test_get_user_by_id(async_session: AsyncSession):
    """Test retrieving a user by ID"""
    # Arrange
    user_data = UserCreate(
        email="test@example.com",
        password="password123",
        is_active=True
    )
    created_user = await create_user(async_session, user_data)
    
    # Act
    retrieved_user = await get_user_by_id(async_session, created_user.id)
    
    # Assert
    assert retrieved_user is not None
    assert retrieved_user.id == created_user.id
    assert retrieved_user.email == "test@example.com"

@pytest.mark.asyncio
async def test_get_users(async_session: AsyncSession):
    """Test retrieving all users"""
    # Arrange
    user1_data = UserCreate(email="user1@example.com", password="pass1")
    user2_data = UserCreate(email="user2@example.com", password="pass2")
    
    await create_user(async_session, user1_data)
    await create_user(async_session, user2_data)
    
    # Act
    users = await get_users(async_session)
    
    # Assert
    assert len(users) == 2
    assert users[0].email == "user1@example.com"
    assert users[1].email == "user2@example.com"

@pytest.mark.asyncio
async def test_update_user(async_session: AsyncSession):
    """Test updating a user"""
    # Arrange
    user_data = UserCreate(
        email="original@example.com",
        password="originalpass",
        is_active=True
    )
    created_user = await create_user(async_session, user_data)
    
    update_data = UserUpdate(
        email="updated@example.com",
        password="newpassword",
        is_active=False
    )
    
    # Act
    updated_user = await update_user(async_session, created_user.id, update_data)
    
    # Assert
    assert updated_user is not None
    assert updated_user.email == "updated@example.com"
    assert updated_user.is_active == False
    assert verify_password("newpassword", updated_user.password)

@pytest.mark.asyncio
async def test_update_user_partial(async_session: AsyncSession):
    """Test partial user update"""
    # Arrange
    user_data = UserCreate(
        email="original@example.com",
        password="originalpass",
        is_active=True
    )
    created_user = await create_user(async_session, user_data)
    
    # Only update email, keep other fields unchanged
    update_data = UserUpdate(email="updated@example.com")
    
    # Act
    updated_user = await update_user(async_session, created_user.id, update_data)
    
    # Assert
    assert updated_user is not None
    assert updated_user.email == "updated@example.com"
    assert updated_user.is_active == True  # Should remain unchanged
    assert verify_password("originalpass", updated_user.password)  # Should remain unchanged

@pytest.mark.asyncio
async def test_delete_user(async_session: AsyncSession):
    """Test deleting a user"""
    # Arrange
    user_data = UserCreate(
        email="delete@example.com",
        password="password123",
        is_active=True
    )
    created_user = await create_user(async_session, user_data)
    
    # Verify user exists
    user_before = await get_user_by_id(async_session, created_user.id)
    assert user_before is not None
    
    # Act
    deleted_user = await delete_user(async_session, created_user.id)
    
    # Assert
    assert deleted_user is not None
    assert deleted_user.id == created_user.id
    
    # Verify user no longer exists
    user_after = await get_user_by_id(async_session, created_user.id)
    assert user_after is None

@pytest.mark.asyncio
async def test_authenticate_user_success(async_session: AsyncSession):
    """Test successful user authentication"""
    # Arrange
    user_data = UserCreate(
        email="test@example.com",
        password="correctpassword",
        is_active=True
    )
    await create_user(async_session, user_data)
    
    # Act
    authenticated_user = await authenticate_user(async_session, "test@example.com", "correctpassword")
    
    # Assert
    assert authenticated_user is not False
    assert authenticated_user.email == "test@example.com"

@pytest.mark.asyncio
async def test_authenticate_user_wrong_password(async_session: AsyncSession):
    """Test authentication with wrong password"""
    # Arrange
    user_data = UserCreate(
        email="test@example.com",
        password="correctpassword",
        is_active=True
    )
    await create_user(async_session, user_data)
    
    # Act
    authenticated_user = await authenticate_user(async_session, "test@example.com", "wrongpassword")
    
    # Assert
    assert authenticated_user is False

@pytest.mark.asyncio
async def test_authenticate_user_not_found(async_session: AsyncSession):
    """Test authentication for non-existent user"""
    # Act
    authenticated_user = await authenticate_user(async_session, "nonexistent@example.com", "anypassword")
    
    # Assert
    assert authenticated_user is False