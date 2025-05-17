import time
import logging
import os
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from pymongo import MongoClient
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# MongoDB connection settings
MONGODB_URI = os.getenv('MONGODB_URI')
DATABASE_NAME = os.getenv('DATABASE_NAME')
COLLECTION_NAME = os.getenv('COLLECTION_NAME')

# List of ballet URLs to update
BALLET_URLS = [
    "https://www.operadeparis.fr/en/season-25-26/ballet/giselle"
]

def setup_driver():
    """Set up and return a configured Chrome WebDriver"""
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
    driver.implicitly_wait(10)  # Wait up to 10 seconds for elements to appear
    driver.set_page_load_timeout(30)  # Wait up to 30 seconds for page to load
    
    # Add webdriver stealth
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': '''
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            })
        '''
    })
    
    return driver

def accept_cookies(driver):
    """Accept cookies on the page if the dialog appears"""
    try:
        # Wait for cookie dialog to be present and visible
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "axeptio_overlay"))
        )
        
        # Try different selectors for accept button
        cookie_button_selectors = [
            (By.ID, "axeptio_btn_acceptAll"),
            (By.CSS_SELECTOR, "[data-test='cookie-accept-all']"),
            (By.CSS_SELECTOR, "button[aria-label*='accept']"),
            (By.XPATH, "//button[contains(text(), 'Accept')]")
        ]
        
        for selector_type, selector in cookie_button_selectors:
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

def save_debug_info(driver, ballet_name):
    """Save debug information when scraping fails"""
    try:
        # Save page source
        with open(f'debug_{ballet_name}_page.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        logger.info(f"Saved page source to debug_{ballet_name}_page.html")
        
        # Save screenshot
        driver.save_screenshot(f'debug_{ballet_name}_screenshot.png')
        logger.info(f"Saved screenshot to debug_{ballet_name}_screenshot.png")
        
        # Log page title and URL
        logger.info(f"Page Title: {driver.title}")
        logger.info(f"Current URL: {driver.current_url}")
    except Exception as e:
        logger.error(f"Failed to save debug info: {str(e)}", exc_info=True)

def scrape_description(driver, url):
    """Scrape the description from the ballet page"""
    try:
        logger.info(f"Navigating to {url}")
        driver.get(url)
        
        logger.info("Handling cookie consent")
        accept_cookies(driver)
        
        logger.info("Waiting for page to load")
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # Let the page settle
        time.sleep(3)
        
        # Extract ballet name from URL for debugging
        ballet_name = url.split('/')[-1]
        
        # Save debug info for analysis
        save_debug_info(driver, ballet_name)
        
        logger.info("Parsing page content")
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Enhanced selectors for description
        description = None
        desc_selectors = [
            # Synopsis section - highest priority
            'div.component-about__left-synopsis div.component-text-max-line__texts',
            'div.component-text-max-line__texts',
            'div#synopsis div.component-text-max-line__texts',
            
            # Primary content selectors
            'div.show__description',
            'div.description',
            'div.performance-description',
            'div.show-description',
            'div.content-description',
            'div[itemprop="description"]',
            
            # Secondary content areas that might contain descriptions
            'div.show__content',
            'div.performance-details',
            'div.about-show',
            'div.show__synopsis',
            'div.synopsis',
            'div.about-performance',
            
            # Text elements that might contain descriptions
            'p.description',
            'p.show-description',
            'p.performance-description',
            
            # Fallback to meta tags
            'meta[property="og:description"]',
            'meta[name="description"]'
        ]
        
        # Try each selector
        for selector in desc_selectors:
            elements = soup.select(selector)
            if elements:
                if selector.startswith('meta'):
                    # For meta tags, get the content attribute
                    content = elements[0].get('content', '')
                    if content and len(content) > 20:  # Ensure it's not too short
                        description = content
                        logger.info(f"Found description in meta tag: {selector}")
                        break
                else:
                    # For regular elements, get the text content
                    content = elements[0].get_text().strip()
                    if content and len(content) > 20:  # Ensure it's not too short
                        description = content
                        logger.info(f"Found description using selector: {selector}")
                        break
        
        # If no description found with selectors, try a more general approach
        if not description:
            logger.info("No description found with specific selectors, trying general content extraction")
            
            # Look for any div with "description" in its class or id
            desc_divs = soup.find_all('div', class_=lambda c: c and 'description' in c.lower())
            if not desc_divs:
                desc_divs = soup.find_all('div', id=lambda i: i and 'description' in i.lower())
            
            if desc_divs:
                content = desc_divs[0].get_text().strip()
                if content and len(content) > 20:
                    description = content
                    logger.info("Found description using general div search")
            
            # If still not found, look for any paragraph that might be a description
            if not description:
                # Find all paragraphs with substantial text
                paragraphs = soup.find_all('p')
                for p in paragraphs:
                    content = p.get_text().strip()
                    if content and len(content) > 100:  # Longer text is more likely to be a description
                        description = content
                        logger.info("Found potential description in paragraph")
                        break
        
        if description:
            logger.info(f"Description found ({len(description)} characters):")
            logger.info(description[:200] + "..." if len(description) > 200 else description)
            return description
        else:
            logger.warning("No description found on the page")
            return None
            
    except Exception as e:
        logger.error(f"Error scraping description: {str(e)}", exc_info=True)
        return None

def update_database(url, description):
    """Update the database with the scraped description"""
    if not description:
        logger.error("No description found to update")
        return False
    
    try:
        # Connect to MongoDB
        client = MongoClient(MONGODB_URI)
        db = client[DATABASE_NAME]
        collection = db[COLLECTION_NAME]
        
        # Find the performance by URL
        performance = collection.find_one({'url': url})
        
        if not performance:
            logger.error(f"No performance found with URL: {url}")
            return False
        
        # Update the description
        result = collection.update_one(
            {'url': url},
            {'$set': {
                'description': description,
                'last_updated': time.strftime('%Y-%m-%d %H:%M:%S')
            }}
        )
        
        if result.modified_count > 0:
            logger.info("Database updated successfully")
            return True
        else:
            logger.warning("No document was updated (might already have the same description)")
            return False
            
    except Exception as e:
        logger.error(f"Error updating database: {str(e)}", exc_info=True)
        return False

def verify_database_update(url):
    """Verify that the database was updated with the new description"""
    try:
        # Connect to MongoDB
        client = MongoClient(MONGODB_URI)
        db = client[DATABASE_NAME]
        collection = db[COLLECTION_NAME]
        
        # Find the performance by URL
        performance = collection.find_one({'url': url})
        
        if not performance:
            logger.error(f"No performance found with URL: {url}")
            return False
        
        description = performance.get('description', '')
        
        if description and description != "Description not found":
            logger.info(f"Verified database update. Description ({len(description)} characters):")
            logger.info(description[:200] + "..." if len(description) > 200 else description)
            return True
        else:
            logger.error("Description not updated in database")
            return False
            
    except Exception as e:
        logger.error(f"Error verifying database update: {str(e)}", exc_info=True)
        return False

def main():
    """Main function to run the script"""
    driver = None
    success_count = 0
    failure_count = 0
    
    logger.info("Starting description scraper for multiple ballets")
    
    try:
        # Setup WebDriver
        driver = setup_driver()
        
        # Process each ballet URL
        for i, url in enumerate(BALLET_URLS, 1):
            try:
                ballet_name = url.split('/')[-1]
                logger.info(f"\n[{i}/{len(BALLET_URLS)}] Processing ballet: {ballet_name}")
                
                # Scrape the description
                description = scrape_description(driver, url)
                
                if description:
                    # Update the database
                    update_success = update_database(url, description)
                    
                    if update_success:
                        # Verify the update
                        verify_success = verify_database_update(url)
                        
                        if verify_success:
                            logger.info(f"Successfully updated description for {ballet_name}")
                            success_count += 1
                        else:
                            logger.error(f"Failed to verify database update for {ballet_name}")
                            failure_count += 1
                    else:
                        logger.error(f"Failed to update database for {ballet_name}")
                        failure_count += 1
                else:
                    logger.error(f"Failed to scrape description for {ballet_name}")
                    failure_count += 1
                
                # Add a random delay between requests (3-7 seconds) to avoid rate limiting
                if i < len(BALLET_URLS):
                    delay = 3 + random.random() * 4
                    logger.info(f"Waiting {delay:.2f} seconds before next request...")
                    time.sleep(delay)
                    
            except Exception as e:
                logger.error(f"Error processing {url}: {str(e)}", exc_info=True)
                failure_count += 1
                
    except Exception as e:
        logger.error(f"An error occurred during the scraping process: {str(e)}", exc_info=True)
    finally:
        # Clean up resources
        if driver:
            driver.quit()
            logger.info("WebDriver closed")
        
        # Print summary
        logger.info("\n=== Summary ===")
        logger.info(f"Total ballets processed: {len(BALLET_URLS)}")
        logger.info(f"Successful updates: {success_count}")
        logger.info(f"Failed updates: {failure_count}")

if __name__ == "__main__":
    main()
