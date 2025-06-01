import pandas as pd
import numpy as np
import pytest
from app.services.market_analysis_system import MarketAnalysisSystem
from app.services.log_manager import LogManager

@pytest.fixture
def large_sample_data():
    np.random.seed(42)
    size = 1200
    dates = pd.date_range(start='2020-01-01', periods=size, freq='D')
    close = np.cumsum(np.random.randn(size)) + 100
    volume = np.random.randint(1000, 5000, size)
    atr_14 = np.abs(np.random.randn(size)) + 1.5
    data = pd.DataFrame({
        'close': close,
        'volume': volume,
        'atr_14': atr_14
    }, index=dates)
    return data

def test_empty_dataframe():
    log_manager = LogManager(enable_console_logging=False)
    mas = MarketAnalysisSystem("TEST", {}, {}, log_manager)
    empty_df = pd.DataFrame()
    result = mas.run_analysis_pipeline(empty_df, [1])
    assert result == {}

def test_missing_columns(large_sample_data):
    log_manager = LogManager(enable_console_logging=False)
    mas = MarketAnalysisSystem("TEST", {}, {}, log_manager)
    df = large_sample_data.drop(columns=['close'])
    result = mas.run_analysis_pipeline(df, [1])
    # Should handle missing columns gracefully, likely returning empty dict
    assert isinstance(result, dict)

def test_integration_feature_engineering_and_ml_prep(large_sample_data):
    log_manager = LogManager(enable_console_logging=False)
    basic_config = {
        "use_volume_features": True,
        "use_price_std_features": True,
        "enable_feature_engineering": True,
        "prediction_type": "classification",
        "selected_models": ["RandomForestClassifier"]
    }
    advanced_config = {
        "prediction_horizons_config": {1: {"models": ["RandomForestClassifier"]}}
    }
    mas = MarketAnalysisSystem("TEST", basic_config, advanced_config, log_manager)
    df = mas._calculate_daily_return(large_sample_data)
    df = mas._classify_market_state(df)
    df = mas._feature_engineering(df)
    X, y, scaler = mas._prepare_data_for_ml(df, 1, "classification")
    assert not X.empty
    assert not y.empty
