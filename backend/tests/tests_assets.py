import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch, AsyncMock
from decimal import Decimal

from app.models.asset import Asset
from app.schemas.asset import AssetCreate, AssetUpdate
from app.services.asset import (
    get_assets, get_asset, get_asset_by_ticker, create_asset,
    create_asset_from_ticker, update_asset, delete_asset, search_assets_by_ticker
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
        yield session
    
    await engine.dispose()

@pytest.mark.asyncio
async def test_get_assets(async_session: AsyncSession):
    """Test retrieving all assets with pagination"""
    # Create test assets
    assets_data = [
        Asset(ticker="AAPL", name="Apple Inc.", exchange="NASDAQ", currency="USD"),
        Asset(ticker="GOOGL", name="Alphabet Inc.", exchange="NASDAQ", currency="USD"),
        Asset(ticker="MSFT", name="Microsoft Corp.", exchange="NASDAQ", currency="USD"),
    ]
    
    for asset in assets_data:
        async_session.add(asset)
    await async_session.commit()
    
    # Test get_assets with pagination
    assets = await get_assets(async_session, skip=1, limit=2)
    
    assert len(assets) == 2
    assert all(isinstance(asset, Asset) for asset in assets)

@pytest.mark.asyncio
async def test_get_asset(async_session: AsyncSession):
    """Test retrieving a specific asset by ID"""
    # Create test asset
    asset = Asset(
        ticker="AAPL",
        name="Apple Inc.",
        exchange="NASDAQ",
        currency="USD"
    )
    async_session.add(asset)
    await async_session.commit()
    await async_session.refresh(asset)
    
    # Test get_asset
    retrieved_asset = await get_asset(async_session, asset.id)
    
    assert retrieved_asset is not None
    assert retrieved_asset.id == asset.id
    assert retrieved_asset.ticker == "AAPL"
    assert retrieved_asset.name == "Apple Inc."

@pytest.mark.asyncio
async def test_get_asset_not_found(async_session: AsyncSession):
    """Test retrieving a non-existent asset"""
    retrieved_asset = await get_asset(async_session, 99999)
    assert retrieved_asset is None

@pytest.mark.asyncio
async def test_get_asset_by_ticker(async_session: AsyncSession):
    """Test retrieving an asset by ticker"""
    # Create test asset
    asset = Asset(
        ticker="AAPL",
        name="Apple Inc.",
        exchange="NASDAQ",
        currency="USD"
    )
    async_session.add(asset)
    await async_session.commit()
    
    # Test get_asset_by_ticker
    retrieved_asset = await get_asset_by_ticker(async_session, "AAPL")
    
    assert retrieved_asset is not None
    assert retrieved_asset.ticker == "AAPL"
    assert retrieved_asset.name == "Apple Inc."

@pytest.mark.asyncio
async def test_get_asset_by_ticker_case_insensitive(async_session: AsyncSession):
    """Test retrieving asset by ticker with case insensitivity"""
    # Create test asset
    asset = Asset(
        ticker="AAPL",
        name="Apple Inc.",
        exchange="NASDAQ",
        currency="USD"
    )
    async_session.add(asset)
    await async_session.commit()
    
    # Test with lowercase ticker
    retrieved_asset = await get_asset_by_ticker(async_session, "aapl")
    
    assert retrieved_asset is not None
    assert retrieved_asset.ticker == "AAPL"

@pytest.mark.asyncio
async def test_get_asset_by_ticker_not_found(async_session: AsyncSession):
    """Test retrieving a non-existent asset by ticker"""
    retrieved_asset = await get_asset_by_ticker(async_session, "NONEXISTENT")
    assert retrieved_asset is None

@pytest.mark.asyncio
async def test_create_asset(async_session: AsyncSession):
    """Test creating a new asset"""
    asset_data = AssetCreate(
        ticker="TSLA",
        name="Tesla Inc.",
        exchange="NASDAQ",
        currency="USD"
    )
    
    # Test create_asset
    created_asset = await create_asset(async_session, asset_data)
    
    assert created_asset is not None
    assert created_asset.id is not None
    assert created_asset.ticker == "TSLA"
    assert created_asset.name == "Tesla Inc."
    assert created_asset.exchange == "NASDAQ"
    assert created_asset.currency == "USD"

@pytest.mark.asyncio
async def test_create_asset_duplicate_ticker(async_session: AsyncSession):
    """Test creating an asset with duplicate ticker"""
    # Create initial asset
    asset1_data = AssetCreate(
        ticker="AAPL",
        name="Apple Inc.",
        exchange="NASDAQ",
        currency="USD"
    )
    await create_asset(async_session, asset1_data)
    
    # Try to create duplicate
    asset2_data = AssetCreate(
        ticker="AAPL",
        name="Apple Company",  # Different name
        exchange="NYSE",       # Different exchange
        currency="EUR"         # Different currency
    )
    duplicate_asset = await create_asset(async_session, asset2_data)
    
    # Should return existing asset, not create new one
    assert duplicate_asset is not None
    assert duplicate_asset.name == "Apple Inc."  # Original name
    assert duplicate_asset.exchange == "NASDAQ"  # Original exchange

@pytest.mark.asyncio
async def test_create_asset_from_ticker_success(async_session: AsyncSession):
    """Test creating asset from Yahoo Finance ticker successfully"""
    mock_asset_data = AsyncMock()
    mock_asset_data.ticker = "AAPL"
    mock_asset_data.name = "Apple Inc."
    mock_asset_data.exchange = "NASDAQ"
    mock_asset_data.currency = "USD"
    
    with patch('app.services.asset.fetch_asset_data', return_value=mock_asset_data):
        # Test create_asset_from_ticker
        created_asset = await create_asset_from_ticker(async_session, "AAPL")
        
        assert created_asset is not None
        assert created_asset.ticker == "AAPL"
        assert created_asset.name == "Apple Inc."
        assert created_asset.exchange == "NASDAQ"
        assert created_asset.currency == "USD"

@pytest.mark.asyncio
async def test_create_asset_from_ticker_already_exists(async_session: AsyncSession):
    """Test creating asset from ticker when asset already exists"""
    # Create existing asset
    existing_asset = Asset(
        ticker="AAPL",
        name="Apple Inc.",
        exchange="NASDAQ",
        currency="USD"
    )
    async_session.add(existing_asset)
    await async_session.commit()
    
    # Mock Yahoo Finance data (should not be called)
    with patch('app.services.asset.fetch_asset_data') as mock_fetch:
        # Test create_asset_from_ticker
        result_asset = await create_asset_from_ticker(async_session, "AAPL")
        
        # Should return existing asset without calling Yahoo Finance
        mock_fetch.assert_not_called()
        assert result_asset is not None
        assert result_asset.id == existing_asset.id
        assert result_asset.ticker == "AAPL"

@pytest.mark.asyncio
async def test_create_asset_from_ticker_yahoo_failure(async_session: AsyncSession):
    """Test creating asset from ticker when Yahoo Finance fails"""
    with patch('app.services.asset.fetch_asset_data', return_value=None):
        # Test create_asset_from_ticker with Yahoo Finance failure
        result_asset = await create_asset_from_ticker(async_session, "INVALIDTICKER")
        
        assert result_asset is None

@pytest.mark.asyncio
async def test_update_asset(async_session: AsyncSession):
    """Test updating an asset"""
    # Create test asset
    asset = Asset(
        ticker="AAPL",
        name="Apple Inc.",
        exchange="NASDAQ",
        currency="USD"
    )
    async_session.add(asset)
    await async_session.commit()
    await async_session.refresh(asset)
    
    # Test update_asset
    update_data = AssetUpdate(
        name="Apple Company",
        exchange="NYSE",
        current_price=Decimal('150.75')
    )
    updated_asset = await update_asset(async_session, asset.id, update_data)
    
    assert updated_asset is not None
    assert updated_asset.name == "Apple Company"
    assert updated_asset.exchange == "NYSE"
    assert updated_asset.ticker == "AAPL"  # Should remain unchanged

@pytest.mark.asyncio
async def test_update_asset_partial(async_session: AsyncSession):
    """Test partial update of an asset"""
    # Create test asset
    asset = Asset(
        ticker="AAPL",
        name="Apple Inc.",
        exchange="NASDAQ",
        currency="USD"
    )
    async_session.add(asset)
    await async_session.commit()
    await async_session.refresh(asset)
    
    # Test partial update (only name)
    update_data = AssetUpdate(name="Apple Corporation")
    updated_asset = await update_asset(async_session, asset.id, update_data)
    
    assert updated_asset is not None
    assert updated_asset.name == "Apple Corporation"
    assert updated_asset.exchange == "NASDAQ"  # Should remain unchanged
    assert updated_asset.currency == "USD"     # Should remain unchanged

@pytest.mark.asyncio
async def test_update_asset_not_found(async_session: AsyncSession):
    """Test updating a non-existent asset"""
    update_data = AssetUpdate(name="Non-existent Asset")
    updated_asset = await update_asset(async_session, 99999, update_data)
    assert updated_asset is None

@pytest.mark.asyncio
async def test_delete_asset(async_session: AsyncSession):
    """Test deleting an asset"""
    # Create test asset
    asset = Asset(
        ticker="AAPL",
        name="Apple Inc.",
        exchange="NASDAQ",
        currency="USD"
    )
    async_session.add(asset)
    await async_session.commit()
    await async_session.refresh(asset)
    
    # Verify asset exists
    asset_before = await get_asset(async_session, asset.id)
    assert asset_before is not None
    
    # Test delete_asset
    deleted_asset = await delete_asset(async_session, asset.id)
    assert deleted_asset is not None
    
    # Verify asset no longer exists
    asset_after = await get_asset(async_session, asset.id)
    assert asset_after is None

@pytest.mark.asyncio
async def test_delete_asset_not_found(async_session: AsyncSession):
    """Test deleting a non-existent asset"""
    deleted_asset = await delete_asset(async_session, 99999)
    assert deleted_asset is None

@pytest.mark.asyncio
async def test_search_assets_by_ticker(async_session: AsyncSession):
    """Test searching assets by ticker (partial match)"""
    # Create test assets
    assets_data = [
        Asset(ticker="AAPL", name="Apple Inc.", exchange="NASDAQ", currency="USD"),
        Asset(ticker="GOOGL", name="Alphabet Inc.", exchange="NASDAQ", currency="USD"),
        Asset(ticker="MSFT", name="Microsoft Corp.", exchange="NASDAQ", currency="USD"),
        Asset(ticker="APLE", name="Apple Hospitality REIT", exchange="NYSE", currency="USD"),
    ]
    
    for asset in assets_data:
        async_session.add(asset)
    await async_session.commit()
    
    # Test search_assets_by_ticker with partial match
    results = await search_assets_by_ticker(async_session, "AAP")
    
    assert len(results) == 1  # AAPL and APLE
    assert any(asset.ticker == "AAPL" for asset in results)

@pytest.mark.asyncio
async def test_search_assets_by_ticker_case_insensitive(async_session: AsyncSession):
    """Test searching assets by ticker with case insensitivity"""
    # Create test asset
    asset = Asset(ticker="AAPL", name="Apple Inc.", exchange="NASDAQ", currency="USD")
    async_session.add(asset)
    await async_session.commit()
    
    # Test with lowercase search
    results = await search_assets_by_ticker(async_session, "aapl")
    
    assert len(results) == 1
    assert results[0].ticker == "AAPL"

@pytest.mark.asyncio
async def test_search_assets_by_ticker_no_match(async_session: AsyncSession):
    """Test searching assets by ticker with no matches"""
    # Create test asset
    asset = Asset(ticker="AAPL", name="Apple Inc.", exchange="NASDAQ", currency="USD")
    async_session.add(asset)
    await async_session.commit()
    
    # Test with non-matching search
    results = await search_assets_by_ticker(async_session, "XYZ")
    
    assert len(results) == 0

@pytest.mark.asyncio
async def test_search_assets_by_ticker_exact_match(async_session: AsyncSession):
    """Test searching assets by ticker with exact match"""
    # Create test assets
    assets_data = [
        Asset(ticker="AAPL", name="Apple Inc.", exchange="NASDAQ", currency="USD"),
        Asset(ticker="APLE", name="Apple Hospitality REIT", exchange="NYSE", currency="USD"),
    ]
    
    for asset in assets_data:
        async_session.add(asset)
    await async_session.commit()
    
    # Test exact match
    results = await search_assets_by_ticker(async_session, "AAPL")
    
    assert len(results) == 1
    assert results[0].ticker == "AAPL"