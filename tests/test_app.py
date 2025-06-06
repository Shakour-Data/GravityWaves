import pytest
import json
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import app

@pytest.fixture
def client():
    app.app.config['TESTING'] = True
    with app.app.test_client() as client:
        yield client

def test_api_market_status_analysis_success(client):
    payload = {
        "ticker": "AAPL",
        "analysis_date": "2023-01-01",
        "timeframe": "1d",
        "candle_count": 500,
        "investment_horizon": 10,
        "data_source": "yahoo"
    }
    response = client.post('/api/market_status_analysis', data=json.dumps(payload), content_type='application/json')
    assert response.status_code == 200
    data = response.get_json()
    assert "current_market_state" in data
    assert "volatility_regime" in data

def test_api_market_status_analysis_missing_ticker(client):
    payload = {
        "analysis_date": "2023-01-01"
    }
    response = client.post('/api/market_status_analysis', data=json.dumps(payload), content_type='application/json')
    assert response.status_code == 400

def test_api_market_status_analysis_invalid_date(client):
    payload = {
        "ticker": "AAPL",
        "analysis_date": "invalid-date"
    }
    response = client.post('/api/market_status_analysis', data=json.dumps(payload), content_type='application/json')
    assert response.status_code == 400

def test_api_custom_analysis_success(client):
    payload = {
        "ticker": "AAPL",
        "analysis_params": {
            "timeframe": "1d",
            "prediction_horizons": [1, 5, 10],
            "basic_config": {},
            "advanced_config": {}
        }
    }
    response = client.post('/api/custom_analysis', data=json.dumps(payload), content_type='application/json')
    assert response.status_code == 200
    data = response.get_json()
    assert "custom_analysis_results" in data

def test_api_custom_analysis_missing_ticker(client):
    payload = {
        "analysis_params": {}
    }
    response = client.post('/api/custom_analysis', data=json.dumps(payload), content_type='application/json')
    assert response.status_code == 400

def test_api_trading_signals_backtesting_success(client):
    payload = {
        "ticker": "AAPL",
        "backtest_params": {
            "timeframe": "1d"
        }
    }
    response = client.post('/api/trading_signals_backtesting', data=json.dumps(payload), content_type='application/json')
    assert response.status_code == 200
    data = response.get_json()
    assert "backtest_results" in data

def test_api_trading_signals_backtesting_missing_ticker(client):
    payload = {
        "backtest_params": {}
    }
    response = client.post('/api/trading_signals_backtesting', data=json.dumps(payload), content_type='application/json')
    assert response.status_code == 400
