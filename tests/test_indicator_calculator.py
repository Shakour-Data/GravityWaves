import pandas as pd
import pytest
from app.services.indicator_calculator import IndicatorCalculator
from app.services.log_manager import LogManager

@pytest.fixture
def sample_data():
    data = {
        'open': [1, 2, 3, 4, 5, 6, 7],
        'high': [2, 3, 4, 5, 6, 7, 8],
        'low': [0.5, 1, 2, 3, 4, 5, 6],
        'close': [1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5],
        'volume': [100, 150, 200, 250, 300, 350, 400]
    }
    return pd.DataFrame(data)

def test_calculate_single_indicator_sma(sample_data):
    calc = IndicatorCalculator(LogManager(enable_console_logging=False))
    result = calc._calculate_single_indicator(sample_data, 'SMA', {'window': 3})
    assert result is not None
    assert 'SMA_3' in result.name or (hasattr(result, 'columns') and 'SMA_3' in result.columns)

def test_calculate_single_indicator_with_list_params(sample_data):
    calc = IndicatorCalculator(LogManager(enable_console_logging=False))
    result = calc._calculate_single_indicator(sample_data, 'EMA', {'window': [3, 5]})
    assert result is not None
    assert 'EMA_3' in result.columns
    assert 'EMA_5' in result.columns

def test_calculate_single_indicator_empty_data():
    calc = IndicatorCalculator(LogManager(enable_console_logging=False))
    empty_df = pd.DataFrame()
    result = calc._calculate_single_indicator(empty_df, 'RSI', {'window': 14})
    assert result is None

def test_calculate_indicators_for_dataframe(sample_data):
    calc = IndicatorCalculator(LogManager(enable_console_logging=False))
    specs = [
        {'name': 'SMA', 'window': 3},
        {'name': 'RSI', 'window': 14}
    ]
    result_df = calc.calculate_indicators_for_dataframe(sample_data, specs)
    assert not result_df.empty
    assert any(col.startswith('SMA') for col in result_df.columns)
    assert any(col.startswith('RSI') for col in result_df.columns)

def test_calculate_single_indicator_unknown_type(sample_data):
    calc = IndicatorCalculator(LogManager(enable_console_logging=False))
    result = calc._calculate_single_indicator(sample_data, 'UNKNOWN', {})
    assert result is None
