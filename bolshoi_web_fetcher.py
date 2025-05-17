#!/usr/bin/env python3
"""
Bolshoi Web Fetcher

This module handles direct web requests to the Bolshoi Theatre website.
It provides functions to fetch HTML content using both the requests library
and Selenium for JavaScript-heavy pages.

Usage:
    from bolshoi_web_fetcher import fetch_with_requests, fetch_with_selenium, fetch_with_retry

Example:
    html_content = fetch_with_requests("https://www.bolshoi.ru/en/season")
    # or
    html_content = fetch_with_selenium("https://www.bolshoi.ru/en/season")
    # or with retry logic
    html_content = fetch_with_retry("https://www.bolshoi.ru/en/season", use_selenium=True)
"""

import requests
import time
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from bolshoi_config import BASE_URL, HEADERS, REQUEST_DELAY, IMPLICIT_WAIT, PAGE_LOAD_TIMEOUT

# Configure logging
logger = logging.getLogger(__name__)

def fetch_with_requests(url=BASE_URL):
    """
    Fetch HTML content using requests library.
    
    Args:
        url (str): URL to fetch
        
    Returns:
        str: HTML content or None if request fails
    """
    try:
        logger.info(f"Fetching URL: {url}")
        time.sleep(REQUEST_DELAY)  # Respect rate limiting
        response = requests.get(url, headers=HEADERS, timeout=30)
        response.raise_for_status()
        logger.info(f"Successfully fetched URL: {url}, content length: {len(response.text)}")
        return response.text
    except Exception as e:
        logger.error(f"Error fetching URL {url}: {str(e)}")
        return None

def fetch_with_selenium(url=BASE_URL):
    """
    Fetch HTML content using Selenium for JavaScript-heavy pages.
    
    Args:
        url (str): URL to fetch
        
    Returns:
        str: HTML content or None if request fails
    """
    driver = None
    try:
        logger.info(f"Fetching URL with Selenium: {url}")
        
        # Configure Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        # Initialize the Chrome driver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Set timeouts
        driver.implicitly_wait(IMPLICIT_WAIT)
        driver.set_page_load_timeout(PAGE_LOAD_TIMEOUT)
        
        # Navigate to the URL
        driver.get(url)
        
        # Wait for the page to load completely
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # Allow JavaScript to execute and render content
        time.sleep(5)
        
        # Get the page source
        html_content = driver.page_source
        logger.info(f"Successfully fetched URL with Selenium: {url}, content length: {len(html_content)}")
        return html_content
    
    except Exception as e:
        logger.error(f"Error fetching URL with Selenium {url}: {str(e)}")
        return None
    
    finally:
        if driver:
            driver.quit()

def fetch_with_retry(url, use_selenium=False, max_retries=3, retry_delay=5):
    """
    Fetch URL with retry logic.
    
    Args:
        url (str): URL to fetch
        use_selenium (bool): Whether to use Selenium
        max_retries (int): Maximum number of retry attempts
        retry_delay (int): Delay between retries in seconds
        
    Returns:
        str: HTML content or None if all retries fail
    """
    for attempt in range(max_retries):
        try:
            if use_selenium:
                html_content = fetch_with_selenium(url)
            else:
                html_content = fetch_with_requests(url)
                
            if html_content:
                return html_content
                
        except Exception as e:
            logger.warning(f"Attempt {attempt+1}/{max_retries} failed: {str(e)}")
            
        # Wait before retrying
        time.sleep(retry_delay)
    
    logger.error(f"All {max_retries} attempts to fetch {url} failed")
    return None

def scrape_all_pages(base_url=BASE_URL, use_selenium=False, max_pages=10):
    """
    Scrape all pages of performances.
    
    Args:
        base_url (str): Base URL to start scraping from
        use_selenium (bool): Whether to use Selenium
        max_pages (int): Maximum number of pages to scrape
        
    Returns:
        list: List of HTML content from all pages
    """
    all_html_contents = []
    
    # Scrape the first page
    html_content = fetch_with_retry(base_url, use_selenium)
    if html_content:
        all_html_contents.append(html_content)
    
    # Check if there are more pages and scrape them
    for page_num in range(2, max_pages + 1):
        page_url = f"{base_url}?page={page_num}"
        logger.info(f"Scraping page {page_num}: {page_url}")
        
        page_html = fetch_with_retry(page_url, use_selenium)
        
        # If no content found, we've reached the end
        if not page_html:
            logger.info(f"No content found on page {page_num}, stopping pagination")
            break
            
        all_html_contents.append(page_html)
        
        # Respect rate limiting
        time.sleep(REQUEST_DELAY * 2)  # Extra delay between pages
    
    return all_html_contents

if __name__ == "__main__":
    # Configure logging for standalone testing
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Test the fetcher
    print("Testing web fetcher...")
    html = fetch_with_requests()
    if html:
        print(f"Successfully fetched HTML with requests, length: {len(html)}")
    else:
        print("Failed to fetch HTML with requests")
