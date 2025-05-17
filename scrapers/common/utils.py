"""
Common utilities for ballet scrapers.

This module provides shared utility functions for all ballet company scrapers,
including HTTP request handling, date parsing, and other common operations.
"""

import time
import random
import logging
import re
from datetime import datetime
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Configure logging
logger = logging.getLogger(__name__)

def setup_selenium_driver():
    """
    Set up a Selenium WebDriver with Chrome.
    
    Returns:
        WebDriver: A configured Chrome WebDriver instance
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # Add more realistic headers
    chrome_options.add_argument('--accept-language=en-US,en;q=0.9')
    chrome_options.add_argument('--accept=text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(10)  # seconds
    driver.set_page_load_timeout(30)  # seconds
    
    # Add webdriver stealth
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': '''
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            })
        '''
    })
    
    return driver

def fetch_with_requests(url, headers=None, retries=3, delay=2):
    """
    Fetch a URL using the requests library with retries.
    
    Args:
        url (str): URL to fetch
        headers (dict, optional): HTTP headers
        retries (int, optional): Number of retry attempts
        delay (int, optional): Delay between retries in seconds
        
    Returns:
        str: HTML content or empty string if failed
    """
    if headers is None:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
        }
    
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            logger.error(f"Attempt {attempt+1}/{retries} failed: {str(e)}")
            if attempt < retries - 1:
                # Add jitter to delay
                jitter = random.uniform(0.5, 1.5)
                sleep_time = delay * jitter
                logger.info(f"Retrying in {sleep_time:.2f} seconds...")
                time.sleep(sleep_time)
            else:
                logger.error(f"Failed to fetch {url} after {retries} attempts")
                return ""
    
    return ""

def fetch_with_selenium(url, driver=None, close_driver=True):
    """
    Fetch a URL using Selenium for JavaScript-heavy pages.
    
    Args:
        url (str): URL to fetch
        driver (WebDriver, optional): Selenium WebDriver instance
        close_driver (bool, optional): Whether to close the driver after fetching
        
    Returns:
        str: HTML content or empty string if failed
    """
    own_driver = False
    if driver is None:
        driver = setup_selenium_driver()
        own_driver = True
    
    try:
        logger.info(f"Navigating to {url}")
        driver.get(url)
        
        # Wait for page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # Let JavaScript execute
        time.sleep(2)
        
        html_content = driver.page_source
        logger.info(f"Successfully fetched {url}")
        return html_content
    except Exception as e:
        logger.error(f"Error fetching {url} with Selenium: {str(e)}")
        return ""
    finally:
        if own_driver and close_driver:
            driver.quit()

def parse_date_range(date_str):
    """
    Parse a date range string into start and end dates.
    
    Args:
        date_str (str): Date range string
        
    Returns:
        tuple: (start_date, end_date) as datetime objects or (None, None) if parsing fails
    """
    if not date_str:
        return None, None
    
    # Try different date range patterns
    
    # Pattern: "from 28 Sep to 31 Oct 2025"
    pattern1 = r'from\s+(\d+\s+[A-Za-z]+)\s+to\s+(\d+\s+[A-Za-z]+\s+\d{4})'
    match1 = re.search(pattern1, date_str)
    if match1:
        start_date_str = match1.group(1)
        end_date_str = match1.group(2)
        
        # Extract year from end date
        year_match = re.search(r'\d{4}', end_date_str)
        if year_match:
            year = year_match.group(0)
            # Add year to start date if missing
            if not re.search(r'\d{4}', start_date_str):
                start_date_str = f"{start_date_str} {year}"
        
        try:
            # Try different date formats
            for fmt in ["%d %B %Y", "%d %b %Y"]:
                try:
                    start_date = datetime.strptime(start_date_str, fmt)
                    end_date = datetime.strptime(end_date_str, fmt)
                    return start_date, end_date
                except ValueError:
                    continue
        except Exception as e:
            logger.error(f"Error parsing date range '{date_str}': {str(e)}")
    
    # Pattern: "from 01 to 31 Dec 2025"
    pattern2 = r'from\s+(\d+)\s+to\s+(\d+\s+[A-Za-z]+\s+\d{4})'
    match2 = re.search(pattern2, date_str)
    if match2:
        end_date_str = match2.group(2)
        month_match = re.search(r'([A-Za-z]+)', end_date_str)
        if month_match:
            month = month_match.group(1)
            start_date_str = f"{match2.group(1)} {month}"
            # Extract year and add to start date
            year_match = re.search(r'(\d{4})', end_date_str)
            if year_match:
                year = year_match.group(1)
                start_date_str = f"{start_date_str} {year}"
                
                try:
                    # Try different date formats
                    for fmt in ["%d %B %Y", "%d %b %Y"]:
                        try:
                            start_date = datetime.strptime(start_date_str, fmt)
                            end_date = datetime.strptime(end_date_str, fmt)
                            return start_date, end_date
                        except ValueError:
                            continue
                except Exception as e:
                    logger.error(f"Error parsing date range '{date_str}': {str(e)}")
    
    # Pattern: "23 – 25 May 2025" (Bolshoi format)
    pattern3 = r'(\d+)\s*[–-]\s*(\d+)\s+([A-Za-z]+)\s+(\d{4})'
    match3 = re.search(pattern3, date_str)
    if match3:
        day_start = match3.group(1)
        day_end = match3.group(2)
        month = match3.group(3)
        year = match3.group(4)
        
        try:
            start_date_str = f"{day_start} {month} {year}"
            end_date_str = f"{day_end} {month} {year}"
            
            for fmt in ["%d %B %Y", "%d %b %Y"]:
                try:
                    start_date = datetime.strptime(start_date_str, fmt)
                    end_date = datetime.strptime(end_date_str, fmt)
                    return start_date, end_date
                except ValueError:
                    continue
        except Exception as e:
            logger.error(f"Error parsing Bolshoi date range '{date_str}': {str(e)}")
    
    # Pattern: "19 September 2024 – 23 March 2025" (full date range)
    pattern4 = r'(\d+\s+[A-Za-z]+\s+\d{4})\s*[–-]\s*(\d+\s+[A-Za-z]+\s+\d{4})'
    match4 = re.search(pattern4, date_str)
    if match4:
        start_date_str = match4.group(1)
        end_date_str = match4.group(2)
        
        try:
            for fmt in ["%d %B %Y", "%d %b %Y"]:
                try:
                    start_date = datetime.strptime(start_date_str, fmt)
                    end_date = datetime.strptime(end_date_str, fmt)
                    return start_date, end_date
                except ValueError:
                    continue
        except Exception as e:
            logger.error(f"Error parsing full date range '{date_str}': {str(e)}")
    
    # If all patterns fail, return None
    logger.warning(f"Could not parse date range: {date_str}")
    return None, None

def clean_html(text):
    """
    Clean HTML tags and normalize whitespace in text.
    
    Args:
        text (str): Text to clean
        
    Returns:
        str: Cleaned text
    """
    if not text:
        return ""
    
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def save_debug_info(driver, filename_prefix="debug"):
    """
    Save debug information when scraping fails.
    
    Args:
        driver (WebDriver): Selenium WebDriver instance
        filename_prefix (str, optional): Prefix for debug files
    """
    try:
        # Save page source
        with open(f'{filename_prefix}_page.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        logger.info(f"Saved page source to {filename_prefix}_page.html")
        
        # Save screenshot
        driver.save_screenshot(f'{filename_prefix}_screenshot.png')
        logger.info(f"Saved screenshot to {filename_prefix}_screenshot.png")
        
        # Log page title and URL
        logger.info(f"Page Title: {driver.title}")
        logger.info(f"Current URL: {driver.current_url}")
    except Exception as e:
        logger.error(f"Failed to save debug info: {str(e)}")

def accept_cookies(driver, selectors=None):
    """
    Accept cookies on a webpage.
    
    Args:
        driver (WebDriver): Selenium WebDriver instance
        selectors (list, optional): List of (By, selector) tuples to try
    """
    if selectors is None:
        selectors = [
            (By.ID, "axeptio_overlay"),
            (By.ID, "axeptio_btn_acceptAll"),
            (By.CSS_SELECTOR, "[data-test='cookie-accept-all']"),
            (By.CSS_SELECTOR, "button[aria-label*='accept']"),
            (By.XPATH, "//button[contains(text(), 'Accept')]"),
            (By.XPATH, "//button[contains(text(), 'Accept All')]"),
            (By.XPATH, "//button[contains(text(), 'I Agree')]")
        ]
    
    try:
        # Wait for cookie dialog to be present
        for selector_type, selector in selectors[:1]:  # Just the first one to detect overlay
            try:
                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((selector_type, selector))
                )
                break
            except Exception:
                continue
        
        # Try different selectors for accept button
        for selector_type, selector in selectors[1:]:  # Skip the first one (overlay)
            try:
                button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((selector_type, selector))
                )
                # Add a small delay before clicking
                time.sleep(1)
                button.click()
                logger.info(f"Cookies accepted successfully using selector: {selector}")
                time.sleep(2)  # Wait for cookie dialog to disappear
                return
            except Exception:
                continue
        
        logger.warning("Could not find cookie accept button with any selector")
    except Exception as e:
        logger.warning(f"Failed to accept cookies: {str(e)}")
