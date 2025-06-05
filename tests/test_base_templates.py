import unittest
from flask import template_rendered
from contextlib import contextmanager
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app

@contextmanager
def captured_templates(app):
    recorded = []

    def record(sender, template, context, **extra):
        recorded.append((template, context))

    template_rendered.connect(record, app)
    try:
        yield recorded
    finally:
        template_rendered.disconnect(record, app)

class BaseTemplatesTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()

    def test_base_template_renders(self):
        with captured_templates(app) as templates:
            response = self.client.get('/')
            self.assertEqual(response.status_code, 200)
            self.assertTrue(any(t.name == 'index.html' for t, ctx in templates))

    def test_header_included(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Stock Market Prediction Logo', response.get_data(as_text=True))

    def test_navbar_included(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Analysis Products', response.get_data(as_text=True))

    def test_sidebar_included(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Global Settings', response.get_data(as_text=True))

    def test_footer_included(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('&copy; 2024 Stock Market Prediction', response.get_data(as_text=True))

if __name__ == '__main__':
    unittest.main()
