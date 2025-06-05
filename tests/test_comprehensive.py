import unittest
from app import app
import json
from app.services.log_manager import LogManager
import datetime

log_manager = LogManager()

class BaseTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def log_test_result(self, test_name, result, message=""):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] Test: {test_name} - Result: {result}"
        if message:
            log_message += f" - Message: {message}"
        log_manager.info(log_message)

class FrontendRoutesTests(BaseTestCase):
    def test_frontend_routes(self):
        routes = [
            '/', '/index.html', '/index', '/market_status_analysis', '/forecast_analysis',
            '/indicator_analysis', '/optimization_results', '/comparative_results',
            '/custom_analysis', '/about', '/pricing', '/sitemap', '/admin_settings'
        ]
        for route in routes:
            with self.subTest(route=route):
                response = self.app.get(route)
                try:
                    self.assertEqual(response.status_code, 200)
                    if route != '/admin_settings':
                        self.assertIn(b'<html', response.data)
                    self.log_test_result(f"Frontend route {route}", "PASS")
                except AssertionError as e:
                    self.log_test_result(f"Frontend route {route}", "FAIL", str(e))
                    raise

class StaticFilesTests(BaseTestCase):
    def test_static_files(self):
        static_files = [
            'js/persian_date_converter.js',
            'css/base.css',
            'images/-5906631792637626071_121.jpg'
        ]
        for file_path in static_files:
            with self.subTest(file=file_path):
                response = self.app.get(f'/static/{file_path}')
                try:
                    self.assertEqual(response.status_code, 200)
                    self.assertTrue(len(response.data) > 0)
                    self.log_test_result(f"Static file {file_path}", "PASS")
                except AssertionError as e:
                    self.log_test_result(f"Static file {file_path}", "FAIL", str(e))
                    raise

class ApiTests(BaseTestCase):
    def test_api_analyze_valid(self):
        payload = {
            "ticker": "AAPL",
            "data_source": "yahoo",
            "basic_config": {},
            "advanced_config": {}
        }
        response = self.app.post('/api/analyze', data=json.dumps(payload), content_type='application/json')
        try:
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertIn('ticker', data)
            self.assertEqual(data['ticker'], 'AAPL')
            self.log_test_result("API analyze valid", "PASS")
        except AssertionError as e:
            self.log_test_result("API analyze valid", "FAIL", str(e))
            raise

    def test_api_analyze_invalid_ticker(self):
        payload = {
            "ticker": "AAPL$",
            "data_source": "yahoo"
        }
        response = self.app.post('/api/analyze', data=json.dumps(payload), content_type='application/json')
        try:
            self.assertEqual(response.status_code, 400)
            self.log_test_result("API analyze invalid ticker", "PASS")
        except AssertionError as e:
            self.log_test_result("API analyze invalid ticker", "FAIL", str(e))
            raise

    def test_api_optimization_results_valid(self):
        payload = {
            "ticker": "AAPL",
            "optimization_params": {
                "basic_config": {},
                "advanced_config": {}
            }
        }
        response = self.app.post('/api/optimization_results', data=json.dumps(payload), content_type='application/json')
        try:
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertIn('optimization_results', data)
            self.log_test_result("API optimization results valid", "PASS")
        except AssertionError as e:
            self.log_test_result("API optimization results valid", "FAIL", str(e))
            raise

    def test_api_optimization_results_missing_ticker(self):
        payload = {
            "optimization_params": {
                "basic_config": {},
                "advanced_config": {}
            }
        }
        response = self.app.post('/api/optimization_results', data=json.dumps(payload), content_type='application/json')
        try:
            self.assertEqual(response.status_code, 400)
            self.log_test_result("API optimization results missing ticker", "PASS")
        except AssertionError as e:
            self.log_test_result("API optimization results missing ticker", "FAIL", str(e))
            raise

    def test_api_market_status_analysis_valid(self):
        payload = {
            "ticker": "AAPL",
            "analysis_date": "2025-06-04",
            "timeframe": "1d"
        }
        response = self.app.post('/api/market_status_analysis', data=json.dumps(payload), content_type='application/json')
        try:
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertEqual(data['ticker'], "AAPL")
            self.assertEqual(data['analysis_date'], "2025-06-04")
            self.assertEqual(data['timeframe'], "1d")
            self.log_test_result("API market status analysis valid", "PASS")
        except AssertionError as e:
            self.log_test_result("API market status analysis valid", "FAIL", str(e))
            raise

    def test_api_market_status_analysis_missing_fields(self):
        payload = {
            "ticker": "AAPL"
        }
        response = self.app.post('/api/market_status_analysis', data=json.dumps(payload), content_type='application/json')
        try:
            self.assertEqual(response.status_code, 400)
            self.log_test_result("API market status analysis missing fields", "PASS")
        except AssertionError as e:
            self.log_test_result("API market status analysis missing fields", "FAIL", str(e))
            raise

class FrontendComponentTests(BaseTestCase):
    def test_sidebar_presence(self):
        response = self.app.get('/')
        try:
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'id="sidebar"', response.data)
            self.log_test_result("Sidebar presence", "PASS")
        except AssertionError as e:
            self.log_test_result("Sidebar presence", "FAIL", str(e))
            raise

    def test_footer_presence(self):
        response = self.app.get('/')
        try:
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'<footer>', response.data)
            self.log_test_result("Footer presence", "PASS")
        except AssertionError as e:
            self.log_test_result("Footer presence", "FAIL", str(e))
            raise

    def test_header_presence(self):
        response = self.app.get('/')
        try:
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'<header>', response.data)
            self.log_test_result("Header presence", "PASS")
        except AssertionError as e:
            self.log_test_result("Header presence", "FAIL", str(e))
            raise

    def test_css_files_loaded(self):
        css_files = [
            'css/base.css',
            'css/footer.css',
            'css/header.css',
            'css/sidebar.css'
        ]
        for css_file in css_files:
            with self.subTest(css_file=css_file):
                response = self.app.get(f'/static/{css_file}')
                try:
                    self.assertEqual(response.status_code, 200)
                    self.assertTrue(len(response.data) > 0)
                    self.log_test_result(f"CSS file {css_file} loaded", "PASS")
                except AssertionError as e:
                    self.log_test_result(f"CSS file {css_file} loaded", "FAIL", str(e))
                    raise

if __name__ == '__main__':
    unittest.main()

# Additional detailed tests to be added iteratively to reach ~200 tests as requested
