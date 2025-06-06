import pytest
import json
import re
import base64
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def post_chat_message(client, message):
    return client.post('/api/chatbot', data=json.dumps({'message': message}), content_type='application/json')

def test_price_query(client):
    response = post_chat_message(client, 'Price for AAPL')
    data = response.get_json()
    assert 'reply' in data
    # data['reply'] is a string, but in case it's a dict, get the string value
    reply_text = data['reply'] if isinstance(data['reply'], str) else str(data['reply'])
    assert re.search(r'latest closing price for AAPL', reply_text, re.IGNORECASE)

def test_price_history_default(client):
    response = post_chat_message(client, 'Price history for AAPL')
    data = response.get_json()
    # data['reply'] is a dict containing 'reply_html'
    reply_data = data['reply'] if isinstance(data['reply'], dict) else data['reply']
    assert 'reply_html' in reply_data
    assert '<table' in reply_data['reply_html']

def test_price_history_custom_count(client):
    response = post_chat_message(client, 'Price history for AAPL 10')
    data = response.get_json()
    # data['reply'] is a dict containing 'reply_html'
    reply_data = data['reply'] if isinstance(data['reply'], dict) else data['reply']
    assert 'reply_html' in reply_data
    assert '<table' in reply_data['reply_html']

def test_export_csv(client):
    response = post_chat_message(client, 'Price history for AAPL 5 export csv')
    data = response.get_json()
    # data['reply'] is a dict containing 'reply_html'
    reply_data = data['reply'] if isinstance(data['reply'], dict) else data['reply']
    assert 'reply_html' in reply_data
    assert 'Download AAPL_price_history.csv' in reply_data['reply_html']

def test_export_excel(client):
    response = post_chat_message(client, 'Price history for AAPL 5 export excel')
    data = response.get_json()
    # data['reply'] is a dict containing 'reply_html'
    reply_data = data['reply'] if isinstance(data['reply'], dict) else data['reply']
    assert 'reply_html' in reply_data
    assert 'Download AAPL_price_history.xlsx' in reply_data['reply_html']
