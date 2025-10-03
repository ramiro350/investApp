import yfinance as yf
from app.schemas.asset import YahooFinanceResponse
from typing import Optional
import logging

logger = logging.getLogger(__name__)

async def fetch_asset_data(ticker: str) -> Optional[YahooFinanceResponse]:
    """Fetch asset data from Yahoo Finance API"""
    try:
        stock = yf.Ticker(ticker)
        print(stock)
        info = stock.info
        
        asset_data = YahooFinanceResponse(
            ticker=ticker.upper(),
            name=info.get('longName', ticker),
            exchange=info.get('exchange', 'Unknown'),
            currency=info.get('currency', 'USD'),
            current_price=info.get('currentPrice') or info.get('regularMarketPrice')
        )
        
        return asset_data
    except Exception as e:
        logger.error(f"Error fetching data for ticker {ticker}: {e}")
        return None

async def search_assets(ticker: str) -> list[YahooFinanceResponse]:
    """Search for assets by ticker"""
    assets = []
    
    # Try exact match first
    exact_match = await fetch_asset_data(ticker)
    if exact_match:
        assets.append(exact_match)
    
    return assets