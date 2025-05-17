"""
Tests for the Boston Ballet scraper.

This module contains tests for the Boston Ballet scraper functionality.
"""

import unittest
from unittest.mock import patch, MagicMock
import os
import sys
import json

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from scrapers.boston_ballet.scraper import (
    scrape_main_page,
    scrape_individual_page,
    add_default_descriptions,
    main_scrape
)
from scrapers.boston_ballet.config import DEFAULT_DESCRIPTIONS

class TestBostonBalletScraper(unittest.TestCase):
    """Test cases for Boston Ballet scraper."""
    
    @patch('scrapers.boston_ballet.scraper.setup_selenium_driver')
    @patch('scrapers.boston_ballet.scraper.accept_cookies')
    def test_scrape_main_page(self, mock_accept_cookies, mock_setup_driver):
        """Test scraping the main page."""
        # Mock the Selenium driver
        mock_driver = MagicMock()
        mock_setup_driver.return_value = mock_driver
        
        # Mock page source with sample performance data
        with open(os.path.join(os.path.dirname(__file__), 'test_data', 'main_page.html'), 'r', encoding='utf-8') as f:
            mock_driver.page_source = f.read()
        
        # Mock find_elements to return some elements
        mock_elements = [MagicMock() for _ in range(3)]
        mock_driver.find_elements.return_value = mock_elements
        
        # Call the function
        with patch('scrapers.boston_ballet.scraper.BeautifulSoup') as mock_bs:
            # Mock BeautifulSoup to return a parser that finds performance cards
            mock_soup = MagicMock()
            mock_bs.return_value = mock_soup
            
            # Mock performance cards
            mock_cards = []
            for i in range(3):
                mock_card = MagicMock()
                
                # Mock title element
                mock_title = MagicMock()
                mock_title.text = f"Test Ballet {i+1}"
                mock_card.select_one.side_effect = lambda selector: mock_title if 'title' in selector else None
                
                # Mock link element
                mock_link = MagicMock()
                mock_link.__getitem__.return_value = f"/performances/test-ballet-{i+1}"
                
                # Mock image element
                mock_img = MagicMock()
                mock_img.__getitem__.return_value = f"/images/test-ballet-{i+1}.jpg"
                
                # Set up select_one to return appropriate elements based on selector
                def select_one_side_effect(selector):
                    if 'title' in selector:
                        return mock_title
                    elif 'link' in selector:
                        return mock_link
                    elif 'image' in selector:
                        return mock_img
                    else:
                        return None
                
                mock_card.select_one.side_effect = select_one_side_effect
                mock_cards.append(mock_card)
            
            mock_soup.select.return_value = mock_cards
            
            # Call the function
            performances = scrape_main_page(mock_driver)
            
            # Assertions
            self.assertEqual(len(performances), 3)
            self.assertEqual(performances[0]['title'], "Test Ballet 1")
            self.assertTrue(performances[0]['url'].startswith('https://www.bostonballet.org'))
            self.assertTrue(performances[0]['thumbnail'].startswith('https://www.bostonballet.org'))
            self.assertEqual(performances[0]['company'], 'Boston Ballet')
    
    @patch('scrapers.boston_ballet.scraper.setup_selenium_driver')
    def test_scrape_individual_page(self, mock_setup_driver):
        """Test scraping an individual performance page."""
        # Mock the Selenium driver
        mock_driver = MagicMock()
        mock_setup_driver.return_value = mock_driver
        
        # Mock page source with sample performance data
        with open(os.path.join(os.path.dirname(__file__), 'test_data', 'individual_page.html'), 'r', encoding='utf-8') as f:
            mock_driver.page_source = f.read()
        
        # Call the function
        with patch('scrapers.boston_ballet.scraper.BeautifulSoup') as mock_bs:
            # Mock BeautifulSoup to return a parser that finds description
            mock_soup = MagicMock()
            mock_bs.return_value = mock_soup
            
            # Mock description element
            mock_desc = MagicMock()
            mock_desc.text = "This is a test ballet description."
            
            # Mock iframe elements for video links
            mock_iframe = MagicMock()
            mock_iframe.get.return_value = "https://www.youtube.com/embed/test123"
            
            # Set up find_all to return iframe elements
            mock_soup.find_all.side_effect = lambda tag: [mock_iframe] if tag == 'iframe' else []
            
            # Set up select_one to return description element
            mock_soup.select_one.return_value = mock_desc
            
            # Call the function
            url = "https://www.bostonballet.org/performances/test-ballet"
            details = scrape_individual_page(mock_driver, url)
            
            # Assertions
            self.assertEqual(details['description'], "This is a test ballet description.")
            self.assertEqual(len(details['video_links']), 1)
            self.assertTrue(details['details_scraped'])
    
    def test_add_default_descriptions(self):
        """Test adding default descriptions to performances."""
        # Create test performances with missing descriptions
        performances = [
            {
                'title': 'The Nutcracker',
                'description': 'Description not found'
            },
            {
                'title': 'Swan Lake',
                'description': 'Failed to scrape'
            },
            {
                'title': 'A New Ballet',  # Not in default descriptions
                'description': 'Description not found'
            }
        ]
        
        # Call the function
        updated_performances = add_default_descriptions(performances)
        
        # Assertions
        self.assertEqual(updated_performances[0]['description'], DEFAULT_DESCRIPTIONS['The Nutcracker'])
        self.assertEqual(updated_performances[1]['description'], DEFAULT_DESCRIPTIONS['Swan Lake'])
        self.assertEqual(updated_performances[2]['description'], 'Description not found')  # Unchanged
    
    @patch('scrapers.boston_ballet.scraper.setup_selenium_driver')
    @patch('scrapers.boston_ballet.scraper.get_collection')
    @patch('scrapers.boston_ballet.scraper.store_performances')
    @patch('scrapers.boston_ballet.scraper.scrape_main_page')
    @patch('scrapers.boston_ballet.scraper.scrape_individual_page')
    def test_main_scrape(self, mock_scrape_individual, mock_scrape_main, 
                         mock_store, mock_get_collection, mock_setup_driver):
        """Test the main scraping function."""
        # Mock the Selenium driver
        mock_driver = MagicMock()
        mock_setup_driver.return_value = mock_driver
        
        # Mock collection
        mock_collection = MagicMock()
        mock_get_collection.return_value = mock_collection
        
        # Mock scrape_main_page to return sample performances
        mock_performances = [
            {
                'title': 'Test Ballet 1',
                'url': 'https://www.bostonballet.org/performances/test-ballet-1',
                'thumbnail': 'https://www.bostonballet.org/images/test-ballet-1.jpg',
                'venue': 'Boston Opera House',
                'date': 'May 1 - May 10, 2025',
                'company': 'Boston Ballet',
                'source': 'Boston Ballet Website'
            }
        ]
        mock_scrape_main.return_value = mock_performances
        
        # Mock scrape_individual_page to return sample details
        mock_details = {
            'description': 'This is a test ballet description.',
            'video_links': ['https://www.youtube.com/watch?v=test123'],
            'details': {'price_range': '$40 - $150'},
            'details_scraped': True,
            'last_updated': '2025-05-17 15:30:00'
        }
        mock_scrape_individual.return_value = mock_details
        
        # Mock store_performances to return success
        mock_store.return_value = True
        
        # Call the function
        success = main_scrape()
        
        # Assertions
        self.assertTrue(success)
        mock_scrape_main.assert_called_once()
        mock_scrape_individual.assert_called_once()
        mock_store.assert_called_once()
        mock_driver.quit.assert_called_once()

if __name__ == '__main__':
    unittest.main()
