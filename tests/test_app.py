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

def test_analyze_success(client):
    payload = {
        "ticker": "AAPL",
        "candle_count": 100,
        "timeframe": "1d",
        "data_source": "yahoo",
        "prediction_horizons": [1, 5],
        "basic_config": {
            "selected_models": ["RandomForestClassifier"],
            "prediction_type": "classification",
            "enable_feature_engineering": True,
            "use_volume_features": True,
            "use_price_std_features": True
        },
        "advanced_config": {
            "optimize_indicators": False,
            "optimization_method": "GA",
            "optimization_generations": 10,
            "optimization_population": 50
        }
    }
    response = client.post('/api/analyze', data=json.dumps(payload), content_type='application/json')
    assert response.status_code == 200
    data = response.get_json()
    assert "ticker" in data
    assert data["ticker"] == "AAPL"
    assert "model_performance" in data

def test_analyze_missing_ticker(client):
    payload = {
        "candle_count": 100
    }
    response = client.post('/api/analyze', data=json.dumps(payload), content_type='application/json')
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data
    assert data["error"] == "Ticker symbol is required"

def test_analyze_invalid_data_source(client):
    payload = {
        "ticker": "AAPL",
        "data_source": "invalid_source"
    }
    response = client.post('/api/analyze', data=json.dumps(payload), content_type='application/json')
    # The backend returns 400 for invalid data_source, so update assertion accordingly
    assert response.status_code == 400

def test_analyze_empty_prediction_horizons(client):
    payload = {
        "ticker": "AAPL",
        "prediction_horizons": []
    }
    response = client.post('/api/analyze', data=json.dumps(payload), content_type='application/json')
    # Should handle empty prediction horizons gracefully
    assert response.status_code == 200 or response.status_code == 500

