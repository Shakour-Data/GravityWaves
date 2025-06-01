import pytest
import numpy as np
import pandas as pd
from unittest.mock import MagicMock, patch
from app.services.optimization_engine import IndicatorOptimizer
from app.services.log_manager import LogManager, ConsolePrinter

@pytest.fixture
def sample_market_data():
    size = 1000
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

@pytest.fixture
def indicator_params():
    return [
        {"name": "SMA", "window_choices": [10, 20, 30]},
        {"name": "RSI", "window_choices": [14, 21]}
    ]

def test_empty_indicator_params(sample_market_data):
    log_manager = LogManager(enable_console_logging=False)
    printer = ConsolePrinter()
    calc = MagicMock()
    optimizer = IndicatorOptimizer(
        ticker="TEST",
        market_data=sample_market_data,
        log_manager=log_manager,
        indicator_calculator=calc,
        printer=printer,
        indicator_params=[],
        optimization_method='GA'
    )
    results = optimizer.optimize()
    assert results == {}

def test_encode_decode_consistency(indicator_params):
    log_manager = LogManager(enable_console_logging=False)
    printer = ConsolePrinter()
    calc = MagicMock()
    optimizer = IndicatorOptimizer(
        ticker="TEST",
        market_data=pd.DataFrame(),
        log_manager=log_manager,
        indicator_calculator=calc,
        printer=printer,
        indicator_params=indicator_params
    )
    specs = [
        {"name": "SMA", "window": 20, "window_choices": [10, 20, 30]},
        {"name": "RSI", "window": 14, "window_choices": [14, 21]}
    ]
    encoded = optimizer._encode_individual(specs)
    decoded = optimizer._decode_individual(encoded)
    assert decoded[0]["name"] == "SMA"
    assert decoded[1]["name"] == "RSI"

def test_optimize_with_mocked_methods(indicator_params, sample_market_data):
    log_manager = LogManager(enable_console_logging=False)
    printer = ConsolePrinter()
    calc = MagicMock()
    optimizer = IndicatorOptimizer(
        ticker="TEST",
        market_data=sample_market_data,
        log_manager=log_manager,
        indicator_calculator=calc,
        printer=printer,
        indicator_params=indicator_params,
        optimization_method='Both'
    )
    with patch.object(optimizer, "_run_genetic_algorithm", return_value=(indicator_params, 0.9)) as mock_ga, \
         patch.object(optimizer, "_run_bayesian_optimization", return_value=(indicator_params, 0.95)) as mock_bo:
        results = optimizer.optimize()
        assert 'GA' in results
        assert 'Bayesian' in results
