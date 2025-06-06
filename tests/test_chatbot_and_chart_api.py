import json
import unittest
from app import app

class ChatbotAndChartApiTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_chatbot_api_success(self):
        payload = {"message": "Hello"}
        response = self.app.post('/api/chatbot', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('reply', data)
        self.assertTrue(len(data['reply']) > 0)

    def test_chatbot_api_missing_message(self):
        payload = {}
        response = self.app.post('/api/chatbot', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('reply', data)

    def test_market_data_api_success(self):
        payload = {"ticker": "AAPL", "timeframe": "1d", "candle_count": 10}
        response = self.app.post('/api/market_data', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)
        if data:
            item = data[0]
            self.assertIn('date', item)
            self.assertIn('open', item)
            self.assertIn('high', item)
            self.assertIn('low', item)
            self.assertIn('close', item)
            self.assertIn('volume', item)

    def test_market_data_api_missing_ticker(self):
        payload = {"timeframe": "1d", "candle_count": 10}
        response = self.app.post('/api/market_data', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)

if __name__ == '__main__':
    unittest.main()
