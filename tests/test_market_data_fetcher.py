import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime
import pandas as pd
from app.services.market_data_fetcher import MarketDataFetcher, YahooFinanceDataSource, TSEDataSource
from app.services.log_manager import LogManager

@pytest.fixture
def log_manager():
    return LogManager(enable_console_logging=False)

def test_select_data_source_yahoo(log_manager):
    fetcher = MarketDataFetcher("AAPL", 10, log_manager, data_source="yahoo")
    assert isinstance(fetcher.data_source, YahooFinanceDataSource)

def test_select_data_source_tse(log_manager):
    fetcher = MarketDataFetcher("فولاد", 10, log_manager, data_source="tse")
    assert isinstance(fetcher.data_source, TSEDataSource)

def test_fetch_data_yahoo_success(log_manager):
    fetcher = MarketDataFetcher("AAPL", 10, log_manager, data_source="yahoo")
    with patch.object(YahooFinanceDataSource, "fetch_data", return_value=pd.DataFrame({
        'open': [1,2], 'high': [2,3], 'low': [1,1], 'close': [2,2], 'volume': [100,200]
    })) as mock_fetch:
        data = fetcher.fetch_data()
        assert data is not None
        mock_fetch.assert_called_once()

def test_fetch_data_tse_success(log_manager):
    fetcher = MarketDataFetcher("فولاد", 10, log_manager, data_source="tse")
    with patch.object(TSEDataSource, "fetch_data", return_value=pd.DataFrame({
        'open': [1,2], 'high': [2,3], 'low': [1,1], 'close': [2,2], 'volume': [100,200]
    })) as mock_fetch:
        data = fetcher.fetch_data()
        assert data is not None
        mock_fetch.assert_called_once()

def test_fetch_data_retry_and_fail(log_manager):
    fetcher = MarketDataFetcher("AAPL", 10, log_manager, data_source="yahoo")
    with patch.object(YahooFinanceDataSource, "fetch_data", side_effect=[None, None, None]) as mock_fetch:
        data = fetcher.fetch_data()
        assert data is None
        assert mock_fetch.call_count == 3
