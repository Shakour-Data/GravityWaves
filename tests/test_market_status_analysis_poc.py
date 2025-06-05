import pytest
from bs4 import BeautifulSoup
import app

@pytest.fixture
def client():
    app.app.config['TESTING'] = True
    with app.app.test_client() as client:
        yield client

def test_inputs_removed_from_main_content_but_present_in_sidebar(client):
    response = client.get('/market_status_analysis')
    assert response.status_code == 200
    html = response.data.decode('utf-8')
    soup = BeautifulSoup(html, 'html.parser')

    # Check main content area does NOT contain the inputs
    main_content = soup.find(id='main-content')
    assert main_content is not None

    # Inputs should NOT be in main content
    assert main_content.find(id='global_ticker') is None
    assert main_content.find(id='global_analysis_date') is None
    assert main_content.find(id='global_timeframe') is None

    # Check sidebar contains the inputs
    sidebar = soup.find(id='sidebar')
    assert sidebar is not None

    # Inputs should be present in sidebar
    assert sidebar.find(id='global_ticker') is not None
    assert sidebar.find(id='global_analysis_date') is not None
    assert sidebar.find(id='global_timeframe') is not None
