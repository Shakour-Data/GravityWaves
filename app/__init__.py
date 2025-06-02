import os
from flask import Flask, render_template, jsonify, request
from app.services.log_manager import LogManager
from app.services.market_analysis_system import MarketAnalysisSystem
from app.services.market_data_fetcher import MarketDataFetcher

template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static'))
app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)

log_manager = LogManager()

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/market_status_analysis')
def market_status_analysis():
    return render_template('market_status_analysis.html')

@app.route('/forecast_analysis')
def forecast_analysis():
    return render_template('forecast_analysis.html')

@app.route('/indicator_analysis')
def indicator_analysis():
    return render_template('indicator_analysis.html')

@app.route('/optimization_results')
def optimization_results():
    return render_template('optimization_results.html')

@app.route('/comparative_results')
def comparative_results():
    return render_template('comparative_results.html')

@app.route('/custom_analysis')
def custom_analysis():
    return render_template('custom_analysis.html')

@app.route('/trading_signals_backtesting')
def trading_signals_backtesting():
    return render_template('trading_signals_backtesting.html')

@app.route('/api/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    ticker = data.get('ticker')
    candle_count = data.get('candle_count', 500)
    timeframe = data.get('timeframe', '1d')
    data_source = data.get('data_source', 'yahoo')
    prediction_horizons = data.get('prediction_horizons', [1, 5, 10])
    basic_config = data.get('basic_config', {})
    advanced_config = data.get('advanced_config', {})

    if not ticker:
        return jsonify({'error': 'Ticker symbol is required'}), 400

    # Validate data_source
    if data_source not in ['yahoo', 'tse']:
        return jsonify({'error': "Invalid data source. Must be 'yahoo' or 'tse'."}), 400

    # Validate prediction_horizons
    if not prediction_horizons:
        prediction_horizons = [1, 5, 10]

    try:
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

        # Validate minimum candles fetched
        if len(market_data) < candle_count:
            return jsonify({'error': f'Insufficient market data fetched: requested {candle_count} candles, got {len(market_data)}'}), 400

        default_basic_config = {
            'selected_models': ['RandomForestClassifier'],
            'prediction_type': 'classification',
            'enable_feature_engineering': True,
            'use_volume_features': True,
            'use_price_std_features': True,
            'horizon': max(prediction_horizons) if prediction_horizons else 10,
            'data_source': data_source,
            'timeframe': timeframe,
            'candle_count': candle_count
        }
        merged_basic_config = {**default_basic_config, **basic_config}
        merged_basic_config['horizon'] = max(prediction_horizons) if prediction_horizons else 10

        default_advanced_config = {
            'n_splits': 5,
            'feature_selection_method': 'permutation_importance',
            'prediction_horizons_config': {h: {'models': merged_basic_config.get('selected_models', ['RandomForestClassifier'])} for h in prediction_horizons},
            'optimize_indicators': False,
            'indicator_params': [],
            'excluded_indicators': []
        }
        merged_advanced_config = {**default_advanced_config, **advanced_config}

        mas = MarketAnalysisSystem(
            ticker=ticker,
            basic_config=merged_basic_config,
            advanced_config=merged_advanced_config,
            log_manager=log_manager
        )

        analysis_results = mas.run_analysis_pipeline(market_data, prediction_horizons)

        return jsonify(analysis_results)

    except Exception as e:
        log_manager.error(f"Error in /api/analyze: {e}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/market_status_analysis', methods=['POST'])
def api_market_status_analysis():
    data = request.get_json()
    ticker = data.get('ticker')
    analysis_date = data.get('analysis_date')
    timeframe = data.get('timeframe', '1d')
    candle_count = data.get('candle_count', 500)

    if not ticker:
        return jsonify({'error': 'Ticker symbol is required'}), 400
    if not analysis_date:
        return jsonify({'error': 'Analysis date is required'}), 400

    try:
        from datetime import datetime
        target_date = datetime.strptime(analysis_date, '%Y-%m-%d')
    except Exception:
        return jsonify({'error': 'Invalid analysis date format'}), 400

    try:
        fetcher = MarketDataFetcher(
            ticker=ticker,
            candle_count=candle_count,
            log_manager=log_manager,
            timeframe=timeframe,
            data_source='yahoo',
            target_date=target_date
        )
        market_data = fetcher.fetch_data()
        if market_data is None or market_data.empty:
            return jsonify({'error': 'Failed to fetch market data'}), 500

        # Simple market state classification example
        from app.services.market_analysis_system import MarketAnalysisSystem

        mas = MarketAnalysisSystem(
            ticker=ticker,
            basic_config={},
            advanced_config={},
            log_manager=log_manager
        )

        # Run classification only
        market_data = mas._classify_market_state(market_data)

        current_state = market_data['market_state'].iloc[-1] if not market_data.empty else 'Unknown'
        volatility_regime = market_data['volatility_regime'].iloc[-1] if 'volatility_regime' in market_data.columns else 'Unknown'

        return jsonify({
            'current_market_state': current_state,
            'volatility_regime': volatility_regime
        })

    except Exception as e:
        log_manager.error(f"Error in /api/market_status_analysis: {e}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/indicator_analysis', methods=['POST'])
def api_indicator_analysis():
    data = request.get_json()
    ticker = data.get('ticker')
    timeframe = data.get('timeframe', '1d')
    indicators = data.get('indicators', [])

    if not ticker:
        return jsonify({'error': 'Ticker symbol is required'}), 400
    if not indicators:
        return jsonify({'error': 'Indicators list is required'}), 400

    try:
        fetcher = MarketDataFetcher(
            ticker=ticker,
            candle_count=500,
            log_manager=log_manager,
            timeframe=timeframe,
            data_source='yahoo'
        )
        market_data = fetcher.fetch_data()
        if market_data is None or market_data.empty:
            return jsonify({'error': 'Failed to fetch market data'}), 500

        from app.services.indicator_calculator import IndicatorCalculator

        calc = IndicatorCalculator(log_manager)
        results = {}
        for indicator in indicators:
            name = indicator.get('name')
            params = indicator.get('params', {})
            # Use the correct method name from IndicatorCalculator
            value = calc._calculate_single_indicator(market_data, name, params)
            # Convert pandas Series or DataFrame to JSON serializable format
            if hasattr(value, 'to_dict'):
                results[name] = value.to_dict()
            elif hasattr(value, 'tolist'):
                results[name] = value.tolist()
            else:
                results[name] = value

        def convert_keys_to_str(d):
            if isinstance(d, dict):
                return {str(k): convert_keys_to_str(v) for k, v in d.items()}
            elif isinstance(d, list):
                return [convert_keys_to_str(i) for i in d]
            else:
                return d

        # Convert keys of dicts to strings for JSON serialization
        results_str_keys = {k: convert_keys_to_str(v) for k, v in results.items()}

        return jsonify({'indicator_results': results_str_keys})

    except Exception as e:
        log_manager.error(f"Error in /api/indicator_analysis: {e}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/optimization_results', methods=['POST'])
def api_optimization_results():
    data = request.get_json()
    ticker = data.get('ticker')
    optimization_params = data.get('optimization_params', {})

    if not ticker:
        return jsonify({'error': 'Ticker symbol is required'}), 400

    try:
        from app.services.optimization_engine import IndicatorOptimizer
        from app.services.indicator_calculator import IndicatorCalculator

        fetcher = MarketDataFetcher(
            ticker=ticker,
            candle_count=500,
            log_manager=log_manager,
            timeframe=optimization_params.get('timeframe', '1d'),
            data_source='yahoo'
        )
        market_data = fetcher.fetch_data()
        if market_data is None or market_data.empty:
            return jsonify({'error': 'Failed to fetch market data'}), 500

        calc = IndicatorCalculator(log_manager)
        optimizer = IndicatorOptimizer(
            ticker=ticker,
            market_data=market_data,
            log_manager=log_manager,
            indicator_calculator=calc,
            printer=None,
            indicator_params=optimization_params.get('indicator_params', []),
            optimization_method=optimization_params.get('method', 'GA')
        )
        results = optimizer.optimize()
        return jsonify({'optimization_results': results})

    except Exception as e:
        log_manager.error(f"Error in /api/optimization_results: {e}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/comparative_results', methods=['POST'])
def api_comparative_results():
    data = request.get_json()
    tickers = data.get('tickers', [])
    timeframe = data.get('timeframe', '1d')

    if not tickers:
        return jsonify({'error': 'Tickers list is required'}), 400

    try:
        from app.services.market_analysis_system import MarketAnalysisSystem

        results = {}
        for ticker in tickers:
            fetcher = MarketDataFetcher(
                ticker=ticker,
                candle_count=500,
                log_manager=log_manager,
                timeframe=timeframe,
                data_source='yahoo'
            )
            market_data = fetcher.fetch_data()
            if market_data is None or market_data.empty:
                results[ticker] = {'error': 'Failed to fetch market data'}
                continue

            default_advanced_config = {
                'prediction_horizons_config': {h: {'models': ['RandomForestClassifier']} for h in [1, 5, 10]},
                'optimize_indicators': False,
                'indicator_params': [],
                'excluded_indicators': []
            }
            default_basic_config = {
                'selected_models': ['RandomForestClassifier'],
                'prediction_type': 'classification',
                'enable_feature_engineering': True,
                'use_volume_features': True,
                'use_price_std_features': True,
                'horizon': 10,
                'data_source': 'yahoo',
                'timeframe': timeframe,
                'candle_count': 500
            }

            mas = MarketAnalysisSystem(
                ticker=ticker,
                basic_config=default_basic_config,
                advanced_config=default_advanced_config,
                log_manager=log_manager
            )
            analysis_result = mas.run_analysis_pipeline(market_data, [1, 5, 10])
            results[ticker] = analysis_result

        return jsonify({'comparative_results': results})

    except Exception as e:
        log_manager.error(f"Error in /api/comparative_results: {e}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/custom_analysis', methods=['POST'])
def api_custom_analysis():
    data = request.get_json()
    ticker = data.get('ticker')
    analysis_params = data.get('analysis_params', {})

    if not ticker:
        return jsonify({'error': 'Ticker symbol is required'}), 400

    try:
        from app.services.market_analysis_system import MarketAnalysisSystem

        fetcher = MarketDataFetcher(
            ticker=ticker,
            candle_count=500,
            log_manager=log_manager,
            timeframe=analysis_params.get('timeframe', '1d'),
            data_source='yahoo'
        )
        market_data = fetcher.fetch_data()
        if market_data is None or market_data.empty:
            return jsonify({'error': 'Failed to fetch market data'}), 500

        default_advanced_config = {
            'prediction_horizons_config': {h: {'models': ['RandomForestClassifier']} for h in analysis_params.get('prediction_horizons', [1, 5, 10])},
            'optimize_indicators': False,
            'indicator_params': [],
            'excluded_indicators': []
        }
        default_basic_config = {
            'selected_models': ['RandomForestClassifier'],
            'prediction_type': 'classification',
            'enable_feature_engineering': True,
            'use_volume_features': True,
            'use_price_std_features': True,
            'horizon': max(analysis_params.get('prediction_horizons', [1, 5, 10])),
            'data_source': 'yahoo',
            'timeframe': analysis_params.get('timeframe', '1d'),
            'candle_count': 500
        }

        mas = MarketAnalysisSystem(
            ticker=ticker,
            basic_config={**default_basic_config, **analysis_params.get('basic_config', {})},
            advanced_config={**default_advanced_config, **analysis_params.get('advanced_config', {})},
            log_manager=log_manager
        )
        analysis_results = mas.run_analysis_pipeline(market_data, analysis_params.get('prediction_horizons', [1, 5, 10]))

        return jsonify({'custom_analysis_results': analysis_results})

    except Exception as e:
        log_manager.error(f"Error in /api/custom_analysis: {e}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/trading_signals_backtesting', methods=['POST'])
def api_trading_signals_backtesting():
    data = request.get_json()
    ticker = data.get('ticker')
    backtest_params = data.get('backtest_params', {})

    if not ticker:
        return jsonify({'error': 'Ticker symbol is required'}), 400

    try:
        from app.services.trading_signals import TradingSignalsBacktester

        fetcher = MarketDataFetcher(
            ticker=ticker,
            candle_count=500,
            log_manager=log_manager,
            timeframe=backtest_params.get('timeframe', '1d'),
            data_source='yahoo'
        )
        market_data = fetcher.fetch_data()
        if market_data is None or market_data.empty:
            return jsonify({'error': 'Failed to fetch market data'}), 500

        backtester = TradingSignalsBacktester(
            market_data=market_data,
            backtest_params=backtest_params,
            log_manager=log_manager
        )
        backtest_results = backtester.run_backtest()

        return jsonify({'backtest_results': backtest_results})

    except Exception as e:
        log_manager.error(f"Error in /api/trading_signals_backtesting: {e}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/admin_settings')
def admin_settings():
    return render_template('admin_settings.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/pricing')
def pricing():
    return render_template('pricing.html')

@app.route('/sitemap')
def sitemap():
    return render_template('sitemap.html')
