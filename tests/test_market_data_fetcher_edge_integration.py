import pytest
from unittest.mock import patch, MagicMock
from app.services.market_data_fetcher import MarketDataFetcher, YahooFinanceDataSource, TSEDataSource
from app.services.log_manager import LogManager
import pandas as pd

@pytest.fixture
def log_manager():
    return LogManager(enable_console_logging=False)

def test_invalid_data_source(log_manager):
    with pytest.raises(ValueError):
        MarketDataFetcher("AAPL", 10, log_manager, data_source="invalid_source")

def test_fetch_data_empty_retry(log_manager):
    fetcher = MarketDataFetcher("AAPL", 10, log_manager, data_source="yahoo")
    with patch.object(YahooFinanceDataSource, "fetch_data", side_effect=[None, None, None]) as mock_fetch:
        data = fetcher.fetch_data()
        assert data is None
        assert mock_fetch.call_count == 3

def test_fetch_data_success(log_manager):
    fetcher = MarketDataFetcher("AAPL", 10, log_manager, data_source="yahoo")
    with patch.object(YahooFinanceDataSource, "fetch_data", return_value=pd.DataFrame({
        'open': [1,2], 'high': [2,3], 'low': [1,1], 'close': [2,2], 'volume': [100,200]
    })) as mock_fetch:
        data = fetcher.fetch_data()
        assert data is not None
        mock_fetch.assert_called_once()
