import pytest
import numpy as np
import pandas as pd
from unittest.mock import MagicMock, patch
from app.services.optimization_engine import IndicatorOptimizer
from app.services.indicator_calculator import IndicatorCalculator
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

def test_optimizer_initialization(sample_market_data, indicator_params):
    log_manager = LogManager(enable_console_logging=False)
    printer = ConsolePrinter()
    calc = IndicatorCalculator(log_manager)
    optimizer = IndicatorOptimizer(
        ticker="TEST",
        market_data=sample_market_data,
        log_manager=log_manager,
        indicator_calculator=calc,
        printer=printer,
        indicator_params=indicator_params,
        optimization_method='GA'
    )
    assert optimizer.ticker == "TEST"
    assert optimizer.indicator_params == indicator_params

def test_encode_decode_individual(indicator_params):
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

def test_custom_mutate(indicator_params):
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
    individual = [0, 1]
    mutated, = optimizer._custom_mutate(individual.copy(), indpb=1.0)
    assert mutated != individual

@patch('app.services.optimization_engine.IndicatorOptimizer._run_genetic_algorithm')
@patch('app.services.optimization_engine.IndicatorOptimizer._run_bayesian_optimization')
def test_optimize_methods(mock_bo, mock_ga, indicator_params, sample_market_data):
    log_manager = LogManager(enable_console_logging=False)
    printer = ConsolePrinter()
    calc = IndicatorCalculator(log_manager)
    optimizer = IndicatorOptimizer(
        ticker="TEST",
        market_data=sample_market_data,
        log_manager=log_manager,
        indicator_calculator=calc,
        printer=printer,
        indicator_params=indicator_params,
        optimization_method='Both'
    )
    mock_ga.return_value = (indicator_params, 0.9)
    mock_bo.return_value = (indicator_params, 0.95)
    results = optimizer.optimize()
    assert 'GA' in results
    assert 'Bayesian' in results
