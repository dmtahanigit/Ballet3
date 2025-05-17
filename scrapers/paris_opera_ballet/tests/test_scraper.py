"""
Tests for the Paris Opera Ballet scraper.
"""

import os
import pytest
from unittest.mock import patch, MagicMock
from bs4 import BeautifulSoup

# Import the scraper module
from scrapers.paris_opera_ballet.scraper import (
    scrape_main_page,
    scrape_individual_page,
    add_default_descriptions,
    main_scrape
)

# Sample HTML content for testing
SAMPLE_HTML = """
<html>
<body>
    <div class="FeaturedList__card">
        <p class="show__title">Swan Lake</p>
        <a class="show__link" href="/en/season/ballet/swan-lake">Details</a>
        <img src="https://example.com/swan-lake.jpg" alt="Swan Lake">
        <p class="show__place"><span>Palais Garnier</span></p>
        <p class="show__date"><span>from 10 Dec to 31 Dec 2025</span></p>
    </div>
    <div class="FeaturedList__card">
        <p class="show__title">Giselle</p>
        <a class="show__link" href="/en/season/ballet/giselle">Details</a>
        <img src="https://example.com/giselle.jpg" alt="Giselle">
        <p class="show__place"><span>Opéra Bastille</span></p>
        <p class="show__date"><span>from 15 Jan to 28 Feb 2026</span></p>
    </div>
</body>
</html>
"""

SAMPLE_DETAIL_HTML = """
<html>
<body>
    <div class="show__description">
        This is a beautiful ballet performance featuring the Paris Opera Ballet dancers.
    </div>
    <div class="video-player" data-video-id="abc123"></div>
</body>
</html>
"""

@pytest.fixture
def mock_driver():
    """Create a mock Selenium WebDriver."""
    driver = MagicMock()
    driver.page_source = SAMPLE_HTML
    return driver

@pytest.fixture
def mock_detail_driver():
    """Create a mock Selenium WebDriver for detail pages."""
    driver = MagicMock()
    driver.page_source = SAMPLE_DETAIL_HTML
    return driver

@pytest.fixture
def mock_collection():
    """Create a mock MongoDB collection."""
    collection = MagicMock()
    collection.update_one.return_value = MagicMock()
    return collection

def test_scrape_main_page(mock_driver):
    """Test scraping the main page."""
    performances = scrape_main_page(mock_driver)
    
    # Check that we extracted the correct number of performances
    assert len(performances) == 2
    
    # Check the first performance
    assert performances[0]['title'] == 'Swan Lake'
    assert performances[0]['url'] == 'https://www.operadeparis.fr/en/season/ballet/swan-lake'
    assert performances[0]['venue'] == 'Palais Garnier'
    assert performances[0]['date'] == 'from 10 Dec to 31 Dec 2025'
    assert performances[0]['company'] == 'Paris Opera Ballet'
    
    # Check the second performance
    assert performances[1]['title'] == 'Giselle'
    assert performances[1]['url'] == 'https://www.operadeparis.fr/en/season/ballet/giselle'
    assert performances[1]['venue'] == 'Opéra Bastille'
    assert performances[1]['date'] == 'from 15 Jan to 28 Feb 2026'

def test_scrape_individual_page(mock_detail_driver):
    """Test scraping an individual performance page."""
    url = 'https://www.operadeparis.fr/en/season/ballet/swan-lake'
    details = scrape_individual_page(mock_detail_driver, url)
    
    # Check that we extracted the correct details
    assert details['description'] == 'This is a beautiful ballet performance featuring the Paris Opera Ballet dancers.'
    assert len(details['video_links']) == 1
    assert details['video_links'][0] == 'https://www.youtube.com/watch?v=abc123'
    assert details['details_scraped'] is True

def test_add_default_descriptions():
    """Test adding default descriptions."""
    performances = [
        {'title': 'Swan Lake', 'description': ''},
        {'title': 'Giselle', 'description': 'Custom description'},
        {'title': 'Unknown Ballet', 'description': ''}
    ]
    
    updated_performances = add_default_descriptions(performances)
    
    # Check that default descriptions were added correctly
    assert 'Swan Lake' in updated_performances[0]['description']
    assert updated_performances[1]['description'] == 'Custom description'  # Should not be changed
    assert updated_performances[2]['description'] == ''  # No default available

@patch('scrapers.paris_opera_ballet.scraper.setup_selenium_driver')
@patch('scrapers.paris_opera_ballet.scraper.get_collection')
@patch('scrapers.paris_opera_ballet.scraper.store_performances')
def test_main_scrape(mock_store, mock_get_collection, mock_setup_driver, mock_driver, mock_collection):
    """Test the main scraping function."""
    # Set up mocks
    mock_setup_driver.return_value = mock_driver
    mock_get_collection.return_value = mock_collection
    mock_store.return_value = True
    
    # Mock the individual page scraping
    with patch('scrapers.paris_opera_ballet.scraper.scrape_individual_page') as mock_scrape_individual:
        mock_scrape_individual.return_value = {
            'description': 'Test description',
            'video_links': ['https://www.youtube.com/watch?v=abc123'],
            'details_scraped': True,
            'last_updated': '2025-05-17 15:00:00'
        }
        
        # Run the main scrape function
        result = main_scrape()
        
        # Check that the function returned success
        assert result is True
        
        # Check that the collection was retrieved
        mock_get_collection.assert_called_once()
        
        # Check that performances were stored
        mock_store.assert_called_once()
        
        # Check that individual pages were scraped
        assert mock_scrape_individual.call_count == 2
