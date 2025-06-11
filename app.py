from flask import render_template
from app import app, db
import sys

# Define unique route handlers to avoid conflicts

@app.route('/')
def index_page():
    analyses = [
        {
            "title": "Price History Analysis",
            "short_desc": "Explore historical price data to identify trends and patterns that inform trading decisions.",
            "long_desc": "Explore historical price data to identify trends and patterns that inform trading decisions. This analysis helps traders understand market behavior over time, detect support and resistance levels, and anticipate future price movements based on past performance."
        },
        {
            "title": "State Analysis",
            "short_desc": "Analyze market states to determine bullish, bearish, or neutral conditions for better timing.",
            "long_desc": "Analyze market states to determine bullish, bearish, or neutral conditions for better timing. This analysis evaluates various indicators and market signals to classify the current market environment, aiding traders in adjusting strategies accordingly."
        },
        {
            "title": "Indicator Analysis",
            "short_desc": "Utilize technical indicators like RSI, MACD, and moving averages to gauge market momentum.",
            "long_desc": "Utilize technical indicators like RSI, MACD, and moving averages to gauge market momentum. This analysis provides insights into overbought or oversold conditions, trend strength, and potential reversal points, enhancing decision-making."
        },
        {
            "title": "Market Dashboard",
            "short_desc": "A comprehensive overview of key market metrics and real-time data for quick insights.",
            "long_desc": "A comprehensive overview of key market metrics and real-time data for quick insights. The dashboard consolidates various data points, charts, and alerts to provide a snapshot of market health and opportunities."
        },
        {
            "title": "Comparative Results",
            "short_desc": "Compare performance metrics across different assets or strategies to identify the best options.",
            "long_desc": "Compare performance metrics across different assets or strategies to identify the best options. This analysis helps in portfolio optimization by highlighting strengths and weaknesses of various investments."
        },
        {
            "title": "Trend Analysis",
            "short_desc": "Identify and analyze market trends to capitalize on upward or downward movements.",
            "long_desc": "Identify and analyze market trends to capitalize on upward or downward movements. This analysis focuses on trend direction, strength, and duration to inform entry and exit points."
        },
        {
            "title": "Forecast Analysis",
            "short_desc": "Use predictive models to forecast future price movements and market conditions.",
            "long_desc": "Use predictive models to forecast future price movements and market conditions. This analysis leverages statistical and machine learning techniques to provide probabilistic insights into market behavior."
        },
        {
            "title": "Custom Analysis",
            "short_desc": "Tailor analysis tools and parameters to fit specific trading strategies and preferences.",
            "long_desc": "Tailor analysis tools and parameters to fit specific trading strategies and preferences. This flexible approach allows users to customize indicators, timeframes, and data sources for personalized insights."
        }
    ]
    return render_template('index.html', analyses=analyses)

@app.route('/market_dashboard')
def market_dashboard_page():
    return render_template('market_dashboard.html')

@app.route('/price_history')
def price_history_page():
    return render_template('market_dashboard.html', analysis_page='Price History')

@app.route('/state_analysis')
def state_analysis_page():
    return render_template('market_dashboard.html', analysis_page='State Analysis')

@app.route('/date_analysis')
def date_analysis_page():
    return render_template('market_dashboard.html', analysis_page='Date Analysis')

@app.route('/price_analysis')
def price_analysis_page():
    return render_template('market_dashboard.html', analysis_page='Price Analysis')

@app.route('/indicator_analysis')
def indicator_analysis_page():
    return render_template('market_dashboard.html', analysis_page='Indicator Analysis')

@app.route('/comparative_results')
def comparative_results_page():
    return render_template('market_dashboard.html', analysis_page='Comparative Results')

@app.route('/custom_analysis')
def custom_analysis_page():
    custom_content_boxes = [
        {"title": "Custom Box 1", "description": "Description for custom box 1."},
        {"title": "Custom Box 2", "description": "Description for custom box 2."},
        {"title": "Custom Box 3", "description": "Description for custom box 3."},
        {"title": "Custom Box 4", "description": "Description for custom box 4."},
        {"title": "Custom Box 5", "description": "Description for custom box 5."},
        {"title": "Custom Box 6", "description": "Description for custom box 6."}
    ]
    return render_template('market_dashboard.html', analysis_page='Custom Analysis', content_boxes=custom_content_boxes)

@app.route('/optimization_results')
def optimization_results_page():
    return render_template('market_dashboard.html', analysis_page='Optimization Results')

@app.route('/trend_analysis')
def trend_analysis_page():
    return render_template('market_dashboard.html', analysis_page='Trend Analysis')

@app.route('/trading_signals')
def trading_signals_page():
    # Placeholder route, template may need to be created
    return "<h1>Trading Signals Backtesting Page - Under Construction</h1>"

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--init-db":
        # Initialize the database tables
        with app.app_context():
            db.create_all()
        print("Database tables created successfully.")
        sys.exit(0)

    port = 5002
    if len(sys.argv) > 1 and sys.argv[1] == "--port" and len(sys.argv) > 2:
        try:
            port = int(sys.argv[2])
        except ValueError:
            pass
    app.run(port=port)
