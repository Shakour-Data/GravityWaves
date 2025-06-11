"""
Module: constants.py

This module defines constant values and default specifications used throughout the application,
particularly for technical indicators and market state classification.

Constants:
- DEFAULT_INDICATOR_SPECS: Default parameter specifications for various technical indicators.
- MAX_DAILY_FLUCTUATION: Maximum allowed daily price fluctuation percentage for market state classification.
- ARTICLE_TYPE_IMPACT_ANALYSIS: String constant representing a new article type for impact analysis.
"""

from typing import Dict, Any, List

# Default specifications for technical indicators with typical parameter windows
DEFAULT_INDICATOR_SPECS: Dict[str, Dict[str, Any]] = {
    "SMA": {"window": [10, 20, 50]},  # Simple Moving Average windows
    "EMA": {"window": [10, 20, 50]},  # Exponential Moving Average windows
    "RSI": {"window": [14]},           # Relative Strength Index window
    "MACD": {"window_fast": [12], "window_slow": [26], "window_sign": [9]},  # MACD parameters
    "BollingerBands": {"window": [20], "window_dev": [2]},  # Bollinger Bands parameters
    "ADX": {"window": [14]},           # Average Directional Index window
    "CCI": {"window": [20]},           # Commodity Channel Index window
    "StochasticOscillator": {"window": [14], "smooth_window": [3]},  # Stochastic Oscillator parameters
    "AverageTrueRange": {"window": [14]},  # ATR window
    "OnBalanceVolumeIndicator": {},  # No parameters for OBV
    "MFI": {"window": [14]},          # Money Flow Index window
    "AccDistIndex": {},               # No parameters for Accumulation/Distribution Index
    "VolumeWeightedAveragePrice": {},  # No parameters for VWAP
}

# Maximum allowed daily fluctuation for market state classification (as a percentage)
MAX_DAILY_FLUCTUATION: float = 0.1

# New article type constant for impact analysis
ARTICLE_TYPE_IMPACT_ANALYSIS: str = "impact_analysis"

