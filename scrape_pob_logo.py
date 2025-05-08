import time
import logging
import requests
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration
BASE_URL = "https://www.operadeparis.fr/en"  # Main page is more likely to have the logo
LOGO_SAVE_PATH = "PageTests/Paris Opera Ballet - World Ballets_files/pob-logo.png"

def setup_driver():
    """Set up the Chrome WebDriver with appropriate options."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    # Add realistic headers
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(10)
    driver.set_page_load_timeout(30)
    
    return driver

def accept_cookies(driver):
    """Accept cookies if the dialog appears."""
    try:
        # Wait for cookie dialog
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
                time.sleep(1)
                button.click()
                logger.info(f"Cookies accepted successfully using selector: {selector}")
                time.sleep(2)
                return
            except Exception:
                continue
        
        logger.warning("Could not find cookie accept button with any selector")
    except Exception as e:
        logger.warning(f"Failed to accept cookies: {str(e)}")

def save_debug_info(driver):
    """Save debug information when scraping fails."""
    try:
        with open('debug_logo_page.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        logger.info("Saved page source to debug_logo_page.html")
        
        driver.save_screenshot('debug_logo_screenshot.png')
        logger.info("Saved screenshot to debug_logo_screenshot.png")
        
        logger.info(f"Page Title: {driver.title}")
        logger.info(f"Current URL: {driver.current_url}")
    except Exception as e:
        logger.error(f"Failed to save debug info: {str(e)}", exc_info=True)

def download_image(url, save_path):
    """Download an image from a URL and save it to the specified path."""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        logger.info(f"Image downloaded and saved to {save_path}")
        return True
    except Exception as e:
        logger.error(f"Error downloading image from {url}: {str(e)}", exc_info=True)
        return False

def scrape_logo():
    """Scrape the Paris Opera Ballet logo from their website."""
    driver = setup_driver()
    
    try:
        logger.info(f"Navigating to {BASE_URL}")
        driver.get(BASE_URL)
        
        logger.info("Handling cookie consent")
        accept_cookies(driver)
        
        logger.info("Waiting for page to load")
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # Wait for logo to load
        logger.info("Looking for logo elements")
        
        # Try different selectors for the logo
        logo_selectors = [
            (By.CSS_SELECTOR, ".site-logo img"),
            (By.CSS_SELECTOR, ".logo img"),
            (By.CSS_SELECTOR, "header .logo img"),
            (By.CSS_SELECTOR, "header img[alt*='logo']"),
            (By.CSS_SELECTOR, "img[alt*='Opera']"),
            (By.CSS_SELECTOR, "img[alt*='Ballet']"),
            (By.CSS_SELECTOR, ".header__logo img"),
            (By.XPATH, "//header//img"),
            (By.XPATH, "//img[contains(@alt, 'logo')]"),
            (By.XPATH, "//img[contains(@alt, 'Opera')]"),
            (By.XPATH, "//img[contains(@alt, 'Ballet')]")
        ]
        
        logo_url = None
        
        for selector_type, selector in logo_selectors:
            try:
                logger.info(f"Trying selector: {selector}")
                logo_elements = driver.find_elements(selector_type, selector)
                
                if logo_elements:
                    for logo in logo_elements:
                        try:
                            src = logo.get_attribute('src')
                            if src and (src.endswith('.png') or src.endswith('.jpg') or src.endswith('.svg')):
                                logo_url = src
                                logger.info(f"Found logo URL: {logo_url}")
                                break
                        except Exception as e:
                            logger.warning(f"Error getting src attribute: {str(e)}")
                    
                    if logo_url:
                        break
            except Exception as e:
                logger.warning(f"Selector {selector} failed: {str(e)}")
                continue
        
        if not logo_url:
            # If we couldn't find the logo with selectors, try parsing the page source
            logger.info("Trying to find logo in page source")
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            
            # Look for img tags with 'logo' in alt or src attributes
            for img in soup.find_all('img'):
                src = img.get('src', '')
                alt = img.get('alt', '')
                
                if ('logo' in src.lower() or 'logo' in alt.lower() or 
                    'opera' in alt.lower() or 'ballet' in alt.lower()) and \
                   (src.endswith('.png') or src.endswith('.jpg') or src.endswith('.svg')):
                    logo_url = src
                    logger.info(f"Found logo URL in page source: {logo_url}")
                    break
        
        if not logo_url:
            logger.error("Could not find logo with any selector")
            save_debug_info(driver)
            return False
        
        # Make sure the URL is absolute
        if not logo_url.startswith('http'):
            if logo_url.startswith('//'):
                logo_url = 'https:' + logo_url
            elif logo_url.startswith('/'):
                logo_url = 'https://www.operadeparis.fr' + logo_url
            else:
                logo_url = 'https://www.operadeparis.fr/' + logo_url
        
        logger.info(f"Final logo URL: {logo_url}")
        
        # Download the logo
        success = download_image(logo_url, LOGO_SAVE_PATH)
        
        if success:
            logger.info("Logo successfully downloaded and saved")
            return True
        else:
            logger.error("Failed to download logo")
            return False
        
    except Exception as e:
        logger.error(f"Error in scrape_logo: {str(e)}", exc_info=True)
        save_debug_info(driver)
        return False
    finally:
        driver.quit()
        logger.info("Logo scraping completed")

if __name__ == "__main__":
    logger.info("Starting Paris Opera Ballet logo scraper")
    success = scrape_logo()
    
    if success:
        logger.info("Logo scraping successful")
    else:
        logger.error("Logo scraping failed")
