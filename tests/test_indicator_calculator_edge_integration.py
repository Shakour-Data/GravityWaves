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

def test_empty_dataframe():
    calc = IndicatorCalculator(LogManager(enable_console_logging=False))
    empty_df = pd.DataFrame()
    result = calc.calculate_indicators_for_dataframe(empty_df, [{'name': 'SMA', 'window': 3}])
    assert result.empty

def test_invalid_indicator_name(sample_data):
    calc = IndicatorCalculator(LogManager(enable_console_logging=False))
    specs = [{'name': 'INVALID_INDICATOR', 'window': 3}]
    result = calc.calculate_indicators_for_dataframe(sample_data, specs)
    # Should return original dataframe unchanged except for logging warning
    assert all(col in result.columns for col in sample_data.columns)

def test_integration_multiple_indicators(sample_data):
    calc = IndicatorCalculator(LogManager(enable_console_logging=False))
    specs = [
        {'name': 'SMA', 'window': [3, 5]},
        {'name': 'EMA', 'window': 3},
        {'name': 'RSI', 'window': 14}
    ]
    result = calc.calculate_indicators_for_dataframe(sample_data, specs)
    # Check that new indicator columns are added
    assert any(col.startswith('SMA') for col in result.columns)
    assert any(col.startswith('EMA') for col in result.columns)
    assert any(col.startswith('RSI') for col in result.columns)
