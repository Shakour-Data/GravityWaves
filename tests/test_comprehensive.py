import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app
import json
from app.services.log_manager import LogManager
import datetime

class FrontendRoutesTests(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()

    def test_frontend_routes(self):
        routes = [
            '/', '/index.html', '/index', '/market_status_analysis', '/forecast_analysis',
            '/indicator_analysis', '/optimization_results', '/comparative_results',
            '/custom_analysis', '/about', '/pricing', '/sitemap', '/admin_settings'
        ]
        for route in routes:
            with self.subTest(route=route):
                response = self.app.get(route)
                self.assertEqual(response.status_code, 200)
                if route != '/admin_settings':
                    self.assertIn(b'<html', response.data)

class ApiTests(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()

    def test_api_market_status_analysis_valid(self):
        payload = {
            "ticker": "AAPL",
            "analysis_date": "2025-06-04",
            "timeframe": "1d",
            "candle_count": 50,
            "investment_horizon": 10,
            "data_source": "yahoo"
        }
        response = self.app.post('/api/market_status_analysis', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 200)

    # Other API tests...

if __name__ == '__main__':
    unittest.main()
