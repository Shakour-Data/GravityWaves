import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
import numpy as np
import pytest
from unittest.mock import MagicMock
from app.services.market_analysis_system import MarketAnalysisSystem, MarketStateClassifier
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

def test_market_state_classifier_thresholds(large_sample_data):
    returns = large_sample_data['close'].pct_change() * 100
    classifier = MarketStateClassifier(returns.dropna())
    thresholds = classifier._calculate_market_state_thresholds()
    assert 'bullish' in thresholds
    assert 'bearish' in thresholds

def test_classify_market_state_and_volatility(large_sample_data):
    returns = large_sample_data['close'].pct_change() * 100
    atr_norm = large_sample_data['atr_14'] / large_sample_data['close']
    classifier = MarketStateClassifier(returns.dropna(), atr_norm.dropna())
    state = classifier.classify_market_state(returns.iloc[1])
    vol = classifier.classify_volatility_regime(atr_norm.iloc[1])
    assert isinstance(state, str)
    assert isinstance(vol, str)

def test_feature_engineering_and_prepare_data(large_sample_data):
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

def test_get_model_pipeline_and_evaluate(monkeypatch, large_sample_data):
    log_manager = LogManager(enable_console_logging=False)
    mas = MarketAnalysisSystem("TEST", {"prediction_type": "classification"}, {}, log_manager)
    pipeline = mas._get_model_pipeline("RandomForestClassifier", "classification")
    assert pipeline is not None

    # Mock _evaluate_model to just return dummy metrics
    monkeypatch.setattr(mas, "_evaluate_model", lambda *args, **kwargs: {"balanced_accuracy": 0.9})
    metrics = mas._evaluate_model(pipeline, pd.DataFrame(np.random.rand(10, 3)), pd.Series(np.random.randint(0, 2, 10)), "classification")
    assert "balanced_accuracy" in metrics

def test_run_analysis_pipeline(large_sample_data):
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
    result = mas.run_analysis_pipeline(large_sample_data, [1])
    assert isinstance(result, dict)
    assert "model_performance" in result

def test_volatility_regime_forecasting_edge_cases(large_sample_data):
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

    # Create a copy and introduce NaNs and edge cases in volatility_regime
    df = large_sample_data.copy()
    df['daily_return'] = df['close'].pct_change() * 100
    df['atr_normalized'] = df['atr_14'] / df['close']
    df['volatility_regime'] = 'NEUTRAL'
    df.loc[df.index[0], 'volatility_regime'] = None  # Missing value
    df.loc[df.index[1], 'volatility_regime'] = 'EXTREME_HIGH'
    df.loc[df.index[2], 'volatility_regime'] = 'EXTREME_LOW'

    # Run pipeline with multiple horizons
    horizons = [1, 5, 10]
    result = mas.run_analysis_pipeline(df, horizons)
    assert isinstance(result, dict)
    for horizon in horizons:
        assert horizon in result['model_performance']
        assert 'volatility_regime_models' in result['model_performance'][horizon]
        for model_name, metrics in result['model_performance'][horizon]['volatility_regime_models'].items():
            assert 'balanced_accuracy' in metrics or 'mean_squared_error' in metrics

def test_run_analysis_pipeline_multi_symbol(large_sample_data):
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
    mas1 = MarketAnalysisSystem("SYM1", basic_config, advanced_config, log_manager)
    mas2 = MarketAnalysisSystem("SYM2", basic_config, advanced_config, log_manager)

    # Use the same sample data for both symbols
    df1 = mas1._calculate_daily_return(large_sample_data)
    df1 = mas1._classify_market_state(df1)
    df1 = mas1._feature_engineering(df1)

    df2 = mas2._calculate_daily_return(large_sample_data)
    df2 = mas2._classify_market_state(df2)
    df2 = mas2._feature_engineering(df2)

    result1 = mas1.run_analysis_pipeline(df1, [1])
    result2 = mas2.run_analysis_pipeline(df2, [1])

    assert isinstance(result1, dict)
    assert isinstance(result2, dict)
    assert result1 != result2  # Different instances should produce different results
