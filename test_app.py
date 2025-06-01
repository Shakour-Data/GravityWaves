import pytest
from unittest.mock import patch, MagicMock
import json
import pandas as pd
import numpy as np 
import app as flask_app

@pytest.fixture
def client():
    flask_app.app.config['TESTING'] = True
    with flask_app.app.test_client() as client:
        yield client

def sample_market_data():
    # Generate synthetic OHLCV data with ~1000 rows
    np.random.seed(42)
    length = 1000
    base_price = 100
    dates = pd.date_range(end=pd.Timestamp.today(), periods=length, freq='D')
    price_changes = np.random.normal(loc=0, scale=1, size=length).cumsum()
    close = base_price + price_changes
    open_ = close + np.random.normal(0, 0.5, length)
    high = np.maximum(open_, close) + np.random.uniform(0, 1, length)
    low = np.minimum(open_, close) - np.random.uniform(0, 1, length)
    volume = np.random.randint(1000, 5000, length)

    df = pd.DataFrame({
        'open': open_,
        'high': high,
        'low': low,
        'close': close,
        'volume': volume
    }, index=dates)
    df.index.name = 'Date'
    return df

def sample_analysis_result():
    return {
        "ticker": "AAPL",
        "analysis_date": "2024-06-01",
        "model_performance": {
            1: {
                "RandomForestClassifier": {
                    "balanced_accuracy": 0.85,
                    "f1_weighted": 0.83,
                    "best_params": {},
                    "confusion_matrix": [[50, 10], [8, 32]]
                }
            }
        },
        "forecasts": {
            1: {
                "RandomForestClassifier": {
                    "predicted_market_state": "BULLISH"
                }
            }
        }
    }

@patch('app.MarketDataFetcher.fetch_data')
@patch('app.MarketAnalysisSystem.run_analysis_pipeline')
def test_analyze_success(mock_run_analysis, mock_fetch_data, client):
    mock_fetch_data.return_value = sample_market_data()
    mock_run_analysis.return_value = sample_analysis_result()

    payload = {
        "ticker": "AAPL",
        "candle_count": 1000,
        "timeframe": "1d",
        "data_source": "yahoo",
        "prediction_horizons": [1]
    }
    response = client.post('/api/analyze', data=json.dumps(payload), content_type='application/json')
    assert response.status_code == 200
    data = response.get_json()
    assert data['ticker'] == "AAPL"
    assert "model_performance" in data
    assert "forecasts" in data

def test_analyze_missing_ticker(client):
    payload = {
        "candle_count": 3
    }
    response = client.post('/api/analyze', data=json.dumps(payload), content_type='application/json')
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data
    assert data["error"] == "Ticker symbol is required"

@patch('app.MarketDataFetcher.fetch_data')
def test_analyze_data_fetch_failure(mock_fetch_data, client):
    mock_fetch_data.return_value = None

    payload = {
        "ticker": "AAPL",
        "candle_count": 1000
    }
    response = client.post('/api/analyze', data=json.dumps(payload), content_type='application/json')
    assert response.status_code == 500
    data = response.get_json()
    assert "error" in data
    assert data["error"] == "Failed to fetch market data"

@patch('app.MarketDataFetcher.fetch_data')
@patch('app.MarketAnalysisSystem.run_analysis_pipeline')
def test_analyze_internal_error(mock_run_analysis, mock_fetch_data, client):
    mock_fetch_data.return_value = sample_market_data()
    mock_run_analysis.side_effect = Exception("Unexpected error")

    payload = {
        "ticker": "AAPL",
        "candle_count": 1000
    }
    response = client.post('/api/analyze', data=json.dumps(payload), content_type='application/json')
    assert response.status_code == 500
    data = response.get_json()
    assert "error" in data
    assert data["error"] == "Internal server error"
