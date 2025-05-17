"""
Tests for the Bolshoi Ballet scraper.
"""

import os
import pytest
from unittest.mock import patch, MagicMock
from bs4 import BeautifulSoup
from datetime import datetime

# Import the scraper module
from scrapers.bolshoi_ballet.scraper import (
    extract_ballet_performances_from_html,
    extract_ballet_performances_from_file,
    extract_ballet_performances_from_url,
    scrape_performance_details,
    main_scrape
)

# Sample HTML content for testing
SAMPLE_HTML = """
<html>
<body>
    <div class="performance-card">
        <h3 class="performance-title">Swan Lake</h3>
        <p class="performance-composer">Music by Pyotr Tchaikovsky</p>
        <p class="performance-date">December 10-15, 2025</p>
        <p class="performance-age">6+</p>
        <p class="performance-type">Classical Ballet</p>
        <a href="/en/performances/swan-lake">Details</a>
    </div>
    <div class="performance-card">
        <h3 class="performance-title">The Nutcracker</h3>
        <p class="performance-composer">Music by Pyotr Tchaikovsky</p>
        <p class="performance-date">January 5-10, 2026</p>
        <p class="performance-age">6+</p>
        <p class="performance-type">Classical Ballet</p>
        <a href="/en/performances/the-nutcracker">Details</a>
    </div>
</body>
</html>
"""

SAMPLE_DETAIL_HTML = """
<html>
<body>
    <div class="performance-description">
        This is a beautiful ballet performance by the Bolshoi Ballet.
    </div>
</body>
</html>
"""

@pytest.fixture
def mock_html_file(tmp_path):
    """Create a temporary HTML file for testing."""
    file_path = tmp_path / "bolshoi.html"
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(SAMPLE_HTML)
    return str(file_path)

@pytest.fixture
def mock_collection():
    """Create a mock MongoDB collection."""
    collection = MagicMock()
    collection.update_one.return_value = MagicMock()
    return collection

def test_extract_ballet_performances_from_html():
    """Test extracting ballet performances from HTML content."""
    performances = extract_ballet_performances_from_html(SAMPLE_HTML)
    
    # Check that we extracted the correct number of performances
    assert len(performances) == 2
    
    # Check the first performance
    assert performances[0]['title'] == 'Swan Lake'
    assert performances[0]['composer'] == 'Music by Pyotr Tchaikovsky'
    assert performances[0]['date'] == 'December 10-15, 2025'
    assert performances[0]['age_restriction'] == '6+'
    assert performances[0]['ballet_type'] == 'Classical Ballet'
    assert performances[0]['venue'] == 'Bolshoi Theatre'
    assert performances[0]['company'] == 'Bolshoi Ballet'
    
    # Check the second performance
    assert performances[1]['title'] == 'The Nutcracker'
    assert performances[1]['composer'] == 'Music by Pyotr Tchaikovsky'
    assert performances[1]['date'] == 'January 5-10, 2026'

def test_extract_ballet_performances_from_file(mock_html_file):
    """Test extracting ballet performances from a file."""
    performances = extract_ballet_performances_from_file(mock_html_file)
    
    # Check that we extracted the correct number of performances
    assert len(performances) == 2
    
    # Check the first performance
    assert performances[0]['title'] == 'Swan Lake'
    assert performances[0]['composer'] == 'Music by Pyotr Tchaikovsky'
    assert performances[0]['date'] == 'December 10-15, 2025'

def test_extract_ballet_performances_from_url():
    """Test extracting ballet performances from a URL."""
    with patch('scrapers.bolshoi_ballet.scraper.fetch_with_requests') as mock_fetch:
        mock_fetch.return_value = SAMPLE_HTML
        
        performances = extract_ballet_performances_from_url('https://www.bolshoi.ru/en/season/')
        
        # Check that we extracted the correct number of performances
        assert len(performances) == 2
        
        # Check the first performance
        assert performances[0]['title'] == 'Swan Lake'
        assert performances[0]['composer'] == 'Music by Pyotr Tchaikovsky'
        assert performances[0]['date'] == 'December 10-15, 2025'

def test_scrape_performance_details():
    """Test scraping performance details."""
    with patch('scrapers.bolshoi_ballet.scraper.fetch_with_requests') as mock_fetch:
        mock_fetch.return_value = SAMPLE_DETAIL_HTML
        
        performance = {
            'title': 'Swan Lake',
            'composer': 'Music by Pyotr Tchaikovsky',
            'url': 'https://www.bolshoi.ru/en/performances/swan-lake',
            'details_scraped': False
        }
        
        updated_performance = scrape_performance_details(performance)
        
        # Check that the details were scraped correctly
        assert updated_performance['description'] == 'This is a beautiful ballet performance by the Bolshoi Ballet.'
        assert updated_performance['details_scraped'] is True
        assert 'last_updated' in updated_performance

def test_scrape_performance_details_with_default_description():
    """Test scraping performance details with default description."""
    with patch('scrapers.bolshoi_ballet.scraper.fetch_with_requests') as mock_fetch:
        mock_fetch.return_value = "<html><body></body></html>"  # No description in HTML
        
        performance = {
            'title': 'Swan Lake',
            'composer': 'Music by Pyotr Tchaikovsky',
            'url': 'https://www.bolshoi.ru/en/performances/swan-lake',
            'details_scraped': False
        }
        
        with patch('scrapers.bolshoi_ballet.scraper.DEFAULT_DESCRIPTIONS', {'Swan Lake': 'Default Swan Lake description'}):
            updated_performance = scrape_performance_details(performance)
            
            # Check that the default description was used
            assert updated_performance['description'] == 'Default Swan Lake description'
            assert updated_performance['details_scraped'] is True

@patch('scrapers.bolshoi_ballet.scraper.get_collection')
@patch('scrapers.bolshoi_ballet.scraper.scrape_all_performances')
@patch('scrapers.bolshoi_ballet.scraper.store_performances')
def test_main_scrape(mock_store, mock_scrape_all, mock_get_collection, mock_collection):
    """Test the main scraping function."""
    # Set up mocks
    mock_get_collection.return_value = mock_collection
    mock_scrape_all.return_value = [
        {
            'title': 'Swan Lake',
            'composer': 'Music by Pyotr Tchaikovsky',
            'date': 'December 10-15, 2025',
            'venue': 'Bolshoi Theatre',
            'company': 'Bolshoi Ballet'
        },
        {
            'title': 'The Nutcracker',
            'composer': 'Music by Pyotr Tchaikovsky',
            'date': 'January 5-10, 2026',
            'venue': 'Bolshoi Theatre',
            'company': 'Bolshoi Ballet'
        }
    ]
    mock_store.return_value = True
    
    # Run the main scrape function
    result = main_scrape(use_web=True, use_selenium=False)
    
    # Check that the function returned success
    assert result is True
    
    # Check that the collection was retrieved
    mock_get_collection.assert_called_once()
    
    # Check that performances were scraped and stored
    mock_scrape_all.assert_called_once_with(True, False, None, True)
    mock_store.assert_called_once()

def test_main_scrape_no_performances():
    """Test the main scraping function when no performances are found."""
    with patch('scrapers.bolshoi_ballet.scraper.get_collection') as mock_get_collection:
        mock_get_collection.return_value = MagicMock()
        
        with patch('scrapers.bolshoi_ballet.scraper.scrape_all_performances') as mock_scrape_all:
            mock_scrape_all.return_value = []
            
            # Run the main scrape function
            result = main_scrape()
            
            # Check that the function returned failure
            assert result is False
