from flask import render_template
from app import app, db
import sys

# Define unique route handlers to avoid conflicts

@app.route('/')
def index_page():
    return render_template('market_dashboard.html')

@app.route('/market_dashboard')
def market_dashboard_page():
    return render_template('market_dashboard.html')

@app.route('/price_history')
def price_history_page():
    return render_template('price_history.html')

@app.route('/state_analysis')
def state_analysis_page():
    return render_template('state_analysis.html')

@app.route('/date_analysis')
def date_analysis_page():
    return render_template('date_analysis.html')

@app.route('/price_analysis')
def price_analysis_page():
    return render_template('price_analysis.html')

@app.route('/indicator_analysis')
def indicator_analysis_page():
    return render_template('indicator_analysis.html')

@app.route('/comparative_results')
def comparative_results_page():
    return render_template('comparative_results.html')

@app.route('/custom_analysis')
def custom_analysis_page():
    return render_template('custom_analysis.html')

@app.route('/optimization_results')
def optimization_results_page():
    return render_template('optimization_results.html')

@app.route('/trend_analysis')
def trend_analysis_page():
    return render_template('trend_analysis.html')

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
