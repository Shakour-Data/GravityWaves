from flask import Flask, render_template, jsonify, request
import os
import sys

# Add the app folder to sys.path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.services.log_manager import LogManager
from app.services.market_analysis_system import MarketAnalysisSystem
from app.services.indicator_calculator import IndicatorCalculator
from app.services.market_data_fetcher import MarketDataFetcher
from app.services.cache_manager import CacheManager
from app.services.optimization_engine import IndicatorOptimizer

app = Flask(__name__)

# Initialize LogManager
log_manager = LogManager()

# Initialize CacheManager
cache_manager = CacheManager()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze():
    """
    API endpoint to run market analysis.
    Expects JSON payload with keys:
    - ticker: str
    - candle_count: int
    - timeframe: str (optional, default '1d')
    - data_source: str ('yahoo' or 'tse', optional, default 'yahoo')
    - prediction_horizons: list of ints (optional, default [1,5,10])
    """
    data = request.get_json()
    ticker = data.get('ticker')
    candle_count = data.get('candle_count', 500)
    timeframe = data.get('timeframe', '1d')
    data_source = data.get('data_source', 'yahoo')
    prediction_horizons = data.get('prediction_horizons', [1, 5, 10])

    if not ticker:
        return jsonify({'error': 'Ticker symbol is required'}), 400

    try:
        # Fetch market data
        fetcher = MarketDataFetcher(
            ticker=ticker,
            candle_count=candle_count,
            log_manager=log_manager,
            timeframe=timeframe,
            data_source=data_source
        )
        market_data = fetcher.fetch_data()
        if market_data is None or market_data.empty:
            return jsonify({'error': 'Failed to fetch market data'}), 500

        # Initialize LogManager for analysis system
        analysis_log_manager = log_manager

        # Basic and advanced config placeholders
        basic_config = {
            'ticker': ticker,
            'selected_models': ['RandomForestClassifier'],
            'prediction_type': 'classification',
            'enable_feature_engineering': True,
            'use_volume_features': True,
            'use_price_std_features': True,
            'primary_prediction_model': 'RandomForestClassifier',
            'horizon': max(prediction_horizons),
            'data_source': data_source,
            'timeframe': timeframe,
            'candle_count': candle_count
        }
        advanced_config = {
            'n_splits': 5,
            'feature_selection_method': 'permutation_importance',
            'prediction_horizons_config': {h: {'models': ['RandomForestClassifier']} for h in prediction_horizons},
            'optimize_indicators': False,
            'indicator_params': [],
            'excluded_indicators': []
        }

        # Initialize MarketAnalysisSystem
        mas = MarketAnalysisSystem(
            ticker=ticker,
            basic_config=basic_config,
            advanced_config=advanced_config,
            log_manager=analysis_log_manager
        )

        # Run analysis pipeline
        analysis_results = mas.run_analysis_pipeline(market_data, prediction_horizons)

        return jsonify(analysis_results)

    except Exception as e:
        log_manager.error(f"Error in /api/analyze: {e}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True)
