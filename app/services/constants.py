from typing import Dict, Any, List

# Default specifications for technical indicators
DEFAULT_INDICATOR_SPECS: Dict[str, Dict[str, Any]] = {
    "SMA": {"window": [10, 20, 50]},
    "EMA": {"window": [10, 20, 50]},
    "RSI": {"window": [14]},
    "MACD": {"window_fast": [12], "window_slow": [26], "window_sign": [9]},
    "BollingerBands": {"window": [20], "window_dev": [2]},
    "ADX": {"window": [14]},
    "CCI": {"window": [20]},
    "StochasticOscillator": {"window": [14], "smooth_window": [3]},
    "AverageTrueRange": {"window": [14]},
    "OnBalanceVolumeIndicator": {}, # No parameters for OBV
    "MFI": {"window": [14]},
    "AccDistIndex": {}, # No parameters for A/D Index
    "VolumeWeightedAveragePrice": {}, # No parameters for VWAP
}

# Maximum allowed daily fluctuation for market state classification (as a percentage)
MAX_DAILY_FLUCTUATION: float = 0.1

# New article type constant for impact analysis
ARTICLE_TYPE_IMPACT_ANALYSIS: str = "impact_analysis"

