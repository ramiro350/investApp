import pytest
from unittest.mock import Mock, patch, AsyncMock
from app.services.yahoo_finance import fetch_asset_data, search_assets
from app.schemas.asset import YahooFinanceResponse
from decimal import Decimal

class MockTicker:
    """Mock yfinance Ticker class"""
    def __init__(self, info_data):
        self.info = info_data

@pytest.mark.asyncio
async def test_fetch_asset_data_success():
    """Test successfully fetching asset data from Yahoo Finance"""
    # Mock data for a successful response
    mock_info = {
        'longName': 'Apple Inc.',
        'exchange': 'NASDAQ',
        'currency': 'USD',
        'currentPrice': 150.75,
        'regularMarketPrice': 150.50
    }
    
    with patch('app.services.yahoo_finance.yf.Ticker') as mock_ticker:
        mock_ticker.return_value = MockTicker(mock_info)
        
        # Test fetch_asset_data
        result = await fetch_asset_data('AAPL')
        
        assert result is not None
        assert isinstance(result, YahooFinanceResponse)
        assert result.ticker == 'AAPL'
        assert result.name == 'Apple Inc.'
        assert result.exchange == 'NASDAQ'
        assert result.currency == 'USD'
        assert result.current_price == Decimal('150.75')

@pytest.mark.asyncio
async def test_fetch_asset_data_fallback_to_regular_market_price():
    """Test fetching asset data when currentPrice is not available"""
    # Mock data with only regularMarketPrice
    mock_info = {
        'longName': 'Apple Inc.',
        'exchange': 'NASDAQ',
        'currency': 'USD',
        'regularMarketPrice': 148.25,
        # currentPrice is missing
    }
    
    with patch('app.services.yahoo_finance.yf.Ticker') as mock_ticker:
        mock_ticker.return_value = MockTicker(mock_info)
        
        # Test fetch_asset_data
        result = await fetch_asset_data('AAPL')
        
        assert result is not None
        assert result.current_price == Decimal('148.25')

@pytest.mark.asyncio
async def test_fetch_asset_data_fallback_to_ticker_name():
    """Test fetching asset data when longName is not available"""
    # Mock data with missing longName
    mock_info = {
        'exchange': 'NASDAQ',
        'currency': 'USD',
        'currentPrice': 150.75,
        # longName is missing
    }
    
    with patch('app.services.yahoo_finance.yf.Ticker') as mock_ticker:
        mock_ticker.return_value = MockTicker(mock_info)
        
        # Test fetch_asset_data
        result = await fetch_asset_data('AAPL')
        
        assert result is not None
        assert result.name == 'AAPL'  # Should fallback to ticker
        assert result.exchange == 'NASDAQ'

@pytest.mark.asyncio
async def test_fetch_asset_data_fallback_to_default_exchange():
    """Test fetching asset data when exchange is not available"""
    # Mock data with missing exchange
    mock_info = {
        'longName': 'Apple Inc.',
        'currency': 'USD',
        'currentPrice': 150.75,
        # exchange is missing
    }
    
    with patch('app.services.yahoo_finance.yf.Ticker') as mock_ticker:
        mock_ticker.return_value = MockTicker(mock_info)
        
        # Test fetch_asset_data
        result = await fetch_asset_data('AAPL')
        
        assert result is not None
        assert result.exchange == 'Unknown'  # Should use default
        assert result.currency == 'USD'

@pytest.mark.asyncio
async def test_fetch_asset_data_fallback_to_default_currency():
    """Test fetching asset data when currency is not available"""
    # Mock data with missing currency
    mock_info = {
        'longName': 'Apple Inc.',
        'exchange': 'NASDAQ',
        'currentPrice': 150.75,
        # currency is missing
    }
    
    with patch('app.services.yahoo_finance.yf.Ticker') as mock_ticker:
        mock_ticker.return_value = MockTicker(mock_info)
        
        # Test fetch_asset_data
        result = await fetch_asset_data('AAPL')
        
        assert result is not None
        assert result.currency == 'USD'  # Should use default
        assert result.exchange == 'NASDAQ'

@pytest.mark.asyncio
async def test_fetch_asset_data_no_price_available():
    """Test fetching asset data when no price information is available"""
    # Mock data with no price information
    mock_info = {
        'longName': 'Apple Inc.',
        'exchange': 'NASDAQ',
        'currency': 'USD',
        # Both currentPrice and regularMarketPrice are missing
    }
    
    with patch('app.services.yahoo_finance.yf.Ticker') as mock_ticker:
        mock_ticker.return_value = MockTicker(mock_info)
        
        # Test fetch_asset_data
        result = await fetch_asset_data('AAPL')
        
        assert result is not None
        assert result.current_price is None
        assert result.name == 'Apple Inc.'

@pytest.mark.asyncio
async def test_fetch_asset_data_ticker_uppercase():
    """Test that ticker is converted to uppercase"""
    mock_info = {
        'longName': 'Apple Inc.',
        'exchange': 'NASDAQ',
        'currency': 'USD',
        'currentPrice': 150.75
    }
    
    with patch('app.services.yahoo_finance.yf.Ticker') as mock_ticker:
        mock_ticker.return_value = MockTicker(mock_info)
        
        # Test with lowercase ticker
        result = await fetch_asset_data('aapl')
        
        assert result is not None
        assert result.ticker == 'AAPL'  # Should be uppercase

@pytest.mark.asyncio
async def test_fetch_asset_data_exception_handling():
    """Test exception handling when Yahoo Finance API fails"""
    with patch('app.services.yahoo_finance.yf.Ticker') as mock_ticker:
        # Simulate an exception when creating Ticker
        mock_ticker.side_effect = Exception("API Error")
        
        # Test fetch_asset_data with exception
        result = await fetch_asset_data('INVALIDTICKER')
        
        assert result is None

@pytest.mark.asyncio
async def test_fetch_asset_data_brazilian_ticker():
    """Test fetching data for Brazilian tickers"""
    mock_info = {
        'longName': 'Petróleo Brasileiro S.A. - Petrobras',
        'exchange': 'B3',
        'currency': 'BRL',
        'currentPrice': 35.50
    }
    
    with patch('app.services.yahoo_finance.yf.Ticker') as mock_ticker:
        mock_ticker.return_value = MockTicker(mock_info)
        
        # Test with Brazilian ticker
        result = await fetch_asset_data('PETR4.SA')
        
        assert result is not None
        assert result.ticker == 'PETR4.SA'
        assert result.name == 'Petróleo Brasileiro S.A. - Petrobras'
        assert result.exchange == 'B3'
        assert result.currency == 'BRL'
        assert result.current_price == Decimal('35.50')

@pytest.mark.asyncio
async def test_search_assets_single_match():
    """Test searching assets with exact match"""
    mock_info = {
        'longName': 'Microsoft Corporation',
        'exchange': 'NASDAQ',
        'currency': 'USD',
        'currentPrice': 330.25
    }
    
    with patch('app.services.yahoo_finance.fetch_asset_data') as mock_fetch:
        mock_fetch.return_value = YahooFinanceResponse(
            ticker='MSFT',
            name='Microsoft Corporation',
            exchange='NASDAQ',
            currency='USD',
            current_price=Decimal('330.25')
        )
        
        # Test search_assets
        results = await search_assets('MSFT')
        
        assert len(results) == 1
        assert results[0].ticker == 'MSFT'
        assert results[0].name == 'Microsoft Corporation'

@pytest.mark.asyncio
async def test_search_assets_no_match():
    """Test searching assets with no matches"""
    with patch('app.services.yahoo_finance.fetch_asset_data') as mock_fetch:
        mock_fetch.return_value = None  # No data found
        
        # Test search_assets
        results = await search_assets('NONEXISTENT')
        
        assert len(results) == 0
        assert results == []

@pytest.mark.asyncio
async def test_search_assets_lowercase_ticker():
    """Test searching assets with lowercase ticker"""
    mock_info = {
        'longName': 'Alphabet Inc.',
        'exchange': 'NASDAQ',
        'currency': 'USD',
        'currentPrice': 2800.50
    }
    
    with patch('app.services.yahoo_finance.fetch_asset_data') as mock_fetch:
        mock_fetch.return_value = YahooFinanceResponse(
            ticker='GOOGL',
            name='Alphabet Inc.',
            exchange='NASDAQ',
            currency='USD',
            current_price=Decimal('2800.50')
        )
        
        # Test with lowercase ticker
        results = await search_assets('googl')
        
        assert len(results) == 1
        assert results[0].ticker == 'GOOGL'

@pytest.mark.asyncio
async def test_search_assets_special_characters():
    """Test searching assets with special characters in ticker"""
    mock_info = {
        'longName': 'Vale S.A.',
        'exchange': 'B3',
        'currency': 'BRL',
        'currentPrice': 68.90
    }
    
    with patch('app.services.yahoo_finance.fetch_asset_data') as mock_fetch:
        mock_fetch.return_value = YahooFinanceResponse(
            ticker='VALE3.SA',
            name='Vale S.A.',
            exchange='B3',
            currency='BRL',
            current_price=Decimal('68.90')
        )
        
        # Test with ticker containing special characters
        results = await search_assets('VALE3.SA')
        
        assert len(results) == 1
        assert results[0].ticker == 'VALE3.SA'

@pytest.mark.asyncio
async def test_fetch_asset_data_complete_mock_scenario():
    """Test a complete realistic scenario with all data available"""
    mock_info = {
        'longName': 'Tesla, Inc.',
        'shortName': 'Tesla',
        'exchange': 'NASDAQ',
        'currency': 'USD',
        'currentPrice': 245.80,
        'regularMarketPrice': 245.75,
        'previousClose': 240.50,
        'marketCap': 780000000000,
        'volume': 25000000
    }
    
    with patch('app.services.yahoo_finance.yf.Ticker') as mock_ticker:
        mock_ticker.return_value = MockTicker(mock_info)
        
        # Test fetch_asset_data
        result = await fetch_asset_data('TSLA')
        
        assert result is not None
        assert result.ticker == 'TSLA'
        assert result.name == 'Tesla, Inc.'  # Uses longName
        assert result.exchange == 'NASDAQ'
        assert result.currency == 'USD'
        assert result.current_price == Decimal('245.80')  # Uses currentPrice

@pytest.mark.asyncio
async def test_fetch_asset_data_empty_info():
    """Test fetching asset data with empty info dictionary"""
    with patch('app.services.yahoo_finance.yf.Ticker') as mock_ticker:
        mock_ticker.return_value = MockTicker({})  # Empty info
        
        # Test fetch_asset_data
        result = await fetch_asset_data('EMPTY')
        
        assert result is not None
        assert result.ticker == 'EMPTY'
        assert result.name == 'EMPTY'  # Fallback to ticker
        assert result.exchange == 'Unknown'  # Default
        assert result.currency == 'USD'  # Default
        assert result.current_price is None  # No price available