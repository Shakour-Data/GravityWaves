import unittest
import json
from app import app

class BackendApiTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_trading_signals_backtesting_valid(self):
        payload = {
            "ticker": "AAPL",
            "backtest_params": {
                "start_date": "2023-01-01",
                "end_date": "2023-06-01",
                "strategy": "simple_moving_average"
            }
        }
        response = self.app.post('/api/trading_signals_backtesting',
                                 data=json.dumps(payload),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn("status", data)
        self.assertEqual(data["status"], "success")
        self.assertIn("backtest_results", data)
        self.assertEqual(data["backtest_results"], payload["backtest_params"])

    def test_trading_signals_backtesting_missing_ticker(self):
        payload = {
            "backtest_params": {
                "start_date": "2023-01-01",
                "end_date": "2023-06-01",
                "strategy": "simple_moving_average"
            }
        }
        response = self.app.post('/api/trading_signals_backtesting',
                                 data=json.dumps(payload),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn("error", data)
        self.assertEqual(data["error"], "Missing ticker")

    def test_trading_signals_backtesting_invalid_ticker_format(self):
        payload = {
            "ticker": "AAPL$",
            "backtest_params": {}
        }
        response = self.app.post('/api/trading_signals_backtesting',
                                 data=json.dumps(payload),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn("error", data)
        self.assertEqual(data["error"], "Invalid ticker format")

    def test_trading_signals_backtesting_invalid_backtest_params(self):
        payload = {
            "ticker": "AAPL",
            "backtest_params": "not_a_dict"
        }
        response = self.app.post('/api/trading_signals_backtesting',
                                 data=json.dumps(payload),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn("error", data)
        self.assertEqual(data["error"], "Invalid backtest_params format")

if __name__ == '__main__':
    unittest.main()
