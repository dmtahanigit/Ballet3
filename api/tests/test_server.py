"""
Tests for the Ballet API server.
"""

import json
import pytest
from unittest.mock import patch, MagicMock

from api.server import app

@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def mock_db():
    """Create a mock MongoDB database."""
    with patch('api.server.db') as mock_db:
        yield mock_db

def test_health_check(client):
    """Test the health check endpoint."""
    response = client.get('/api/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'ok'
    assert 'timestamp' in data

def test_get_companies(client):
    """Test getting the list of companies."""
    response = client.get('/api/companies')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) == 2
    assert data[0]['id'] == 'paris_opera_ballet'
    assert data[1]['id'] == 'bolshoi_ballet'

def test_get_all_performances(client, mock_db):
    """Test getting all performances."""
    # Mock the database collections
    mock_db['paris_opera_ballet'].find.return_value = [
        {'title': 'Swan Lake', 'company': 'Paris Opera Ballet'},
        {'title': 'Giselle', 'company': 'Paris Opera Ballet'}
    ]
    mock_db['bolshoi_ballet'].find.return_value = [
        {'title': 'Spartacus', 'company': 'Bolshoi Ballet'},
        {'title': 'The Nutcracker', 'company': 'Bolshoi Ballet'}
    ]
    
    response = client.get('/api/performances')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['total'] == 4
    assert len(data['data']) == 4
    assert data['data'][0]['title'] == 'Swan Lake'
    assert data['data'][2]['title'] == 'Spartacus'

def test_get_company_performances(client, mock_db):
    """Test getting performances for a specific company."""
    # Mock the database collection
    mock_db['paris_opera_ballet'].find.return_value = MagicMock()
    mock_db['paris_opera_ballet'].find.return_value.skip.return_value = MagicMock()
    mock_db['paris_opera_ballet'].find.return_value.skip.return_value.limit.return_value = [
        {'title': 'Swan Lake', 'company': 'Paris Opera Ballet'},
        {'title': 'Giselle', 'company': 'Paris Opera Ballet'}
    ]
    mock_db['paris_opera_ballet'].count_documents.return_value = 2
    
    response = client.get('/api/performances/paris_opera_ballet')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['total'] == 2
    assert len(data['data']) == 2
    assert data['data'][0]['title'] == 'Swan Lake'
    assert data['data'][1]['title'] == 'Giselle'

def test_get_performance(client, mock_db):
    """Test getting a specific performance."""
    # Mock the database collection
    mock_db['paris_opera_ballet'].find_one.return_value = {
        'title': 'Swan Lake',
        'company': 'Paris Opera Ballet',
        'description': 'A beautiful ballet'
    }
    
    response = client.get('/api/performances/paris_opera_ballet/123')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['title'] == 'Swan Lake'
    assert data['company'] == 'Paris Opera Ballet'

def test_get_performance_not_found(client, mock_db):
    """Test getting a performance that doesn't exist."""
    # Mock the database collection
    mock_db['paris_opera_ballet'].find_one.return_value = None
    
    response = client.get('/api/performances/paris_opera_ballet/999')
    assert response.status_code == 404
    data = json.loads(response.data)
    assert 'error' in data

def test_search_performances(client, mock_db):
    """Test searching for performances."""
    # Mock the database collections
    mock_db['paris_opera_ballet'].find.return_value = [
        {'title': 'Swan Lake', 'company': 'Paris Opera Ballet'}
    ]
    mock_db['bolshoi_ballet'].find.return_value = [
        {'title': 'Swan Lake', 'company': 'Bolshoi Ballet'}
    ]
    
    response = client.get('/api/search?q=Swan')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['total'] == 2
    assert len(data['data']) == 2
    assert data['data'][0]['title'] == 'Swan Lake'
    assert data['data'][0]['company'] == 'Paris Opera Ballet'
    assert data['data'][1]['title'] == 'Swan Lake'
    assert data['data'][1]['company'] == 'Bolshoi Ballet'

def test_search_performances_with_company_filter(client, mock_db):
    """Test searching for performances with company filter."""
    # Mock the database collection
    mock_db['paris_opera_ballet'].find.return_value = [
        {'title': 'Swan Lake', 'company': 'Paris Opera Ballet'}
    ]
    
    response = client.get('/api/search?q=Swan&company=paris_opera_ballet')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['total'] == 1
    assert len(data['data']) == 1
    assert data['data'][0]['title'] == 'Swan Lake'
    assert data['data'][0]['company'] == 'Paris Opera Ballet'

def test_search_performances_no_query(client):
    """Test searching for performances without a query."""
    response = client.get('/api/search')
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data

def test_search_performances_invalid_company(client):
    """Test searching for performances with an invalid company."""
    response = client.get('/api/search?q=Swan&company=invalid')
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
