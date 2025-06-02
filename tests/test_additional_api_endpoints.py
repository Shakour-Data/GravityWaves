import pytest
import json

@pytest.fixture
def client():
    from app import app as flask_app
    flask_app.config['TESTING'] = True
    with flask_app.test_client() as client:
        yield client

def test_indicator_analysis_success(client):
    payload = {
        "ticker": "AAPL",
        "indicators": [
            {"name": "SMA", "params": {"window": 14}},
            {"name": "RSI", "params": {"window": 14}}
        ]
    }
    response = client.post('/api/indicator_analysis', data=json.dumps(payload), content_type='application/json')
    assert response.status_code == 200
    data = response.get_json()
    assert "indicator_results" in data
    assert "SMA" in data["indicator_results"]
    assert "RSI" in data["indicator_results"]

def test_indicator_analysis_missing_ticker(client):
    payload = {
        "indicators": [{"name": "SMA", "params": {"window": 14}}]
    }
    response = client.post('/api/indicator_analysis', data=json.dumps(payload), content_type='application/json')
    assert response.status_code == 400

def test_optimization_results_success(client):
    payload = {
        "ticker": "AAPL",
        "optimization_params": {
            "timeframe": "1d",
            "indicator_params": [
                {"name": "SMA", "window_choices": [10, 20]},
                {"name": "RSI", "window_choices": [14, 21]}
            ],
            "method": "GA"
        }
    }
    response = client.post('/api/optimization_results', data=json.dumps(payload), content_type='application/json')
    assert response.status_code == 200
    data = response.get_json()
    assert "optimization_results" in data

def test_optimization_results_missing_ticker(client):
    payload = {
        "optimization_params": {}
    }
    response = client.post('/api/optimization_results', data=json.dumps(payload), content_type='application/json')
    assert response.status_code == 400

def test_comparative_results_success(client):
    payload = {
        "tickers": ["AAPL", "MSFT"],
        "timeframe": "1d"
    }
    response = client.post('/api/comparative_results', data=json.dumps(payload), content_type='application/json')
    assert response.status_code == 200
    data = response.get_json()
    assert "comparative_results" in data
    assert "AAPL" in data["comparative_results"]
    assert "MSFT" in data["comparative_results"]

def test_comparative_results_missing_tickers(client):
    payload = {}
    response = client.post('/api/comparative_results', data=json.dumps(payload), content_type='application/json')
    assert response.status_code == 400

def test_custom_analysis_success(client):
    payload = {
        "ticker": "AAPL",
        "analysis_params": {
            "timeframe": "1d",
            "basic_config": {},
            "advanced_config": {},
            "prediction_horizons": [1, 5]
        }
    }
    response = client.post('/api/custom_analysis', data=json.dumps(payload), content_type='application/json')
    assert response.status_code == 200
    data = response.get_json()
    assert "custom_analysis_results" in data

def test_custom_analysis_missing_ticker(client):
    payload = {
        "analysis_params": {}
    }
    response = client.post('/api/custom_analysis', data=json.dumps(payload), content_type='application/json')
    assert response.status_code == 400

def test_trading_signals_backtesting_success(client):
    payload = {
        "ticker": "AAPL",
        "backtest_params": {
            "timeframe": "1d",
            "strategy": "simple_moving_average"
        }
    }
    response = client.post('/api/trading_signals_backtesting', data=json.dumps(payload), content_type='application/json')
    assert response.status_code == 200
    data = response.get_json()
    assert "backtest_results" in data

def test_trading_signals_backtesting_missing_ticker(client):
    payload = {
        "backtest_params": {}
    }
    response = client.post('/api/trading_signals_backtesting', data=json.dumps(payload), content_type='application/json')
    assert response.status_code == 400
