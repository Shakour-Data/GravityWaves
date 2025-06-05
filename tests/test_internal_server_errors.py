import unittest
from app import app

class TestRootEndpoint(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_root_endpoint(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<html', response.data)  # Basic check for HTML content

    def test_robots_txt(self):
        response = self.app.get('/robots.txt')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, b"User-agent: *\nDisallow:")

if __name__ == '__main__':
    unittest.main()
