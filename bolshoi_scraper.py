#!/usr/bin/env python3
"""
Bolshoi Ballet Scraper

This script scrapes ballet performance data from the Bolshoi Theatre website
and stores it in a MongoDB database. It can work with both locally saved HTML
files and by directly scraping the Bolshoi website.

Usage:
    python bolshoi_scraper.py [options]

Examples:
    # Using a local HTML file
    python bolshoi_scraper.py --html_file "../Bolshoi HTML TEST/Bolshoi Theatre • Season.html" --output "bolshoi_performances.json"
    
    # Scraping directly from the web
    python bolshoi_scraper.py --use_web --output "bolshoi_performances.json"
    
    # Using Selenium for JavaScript-heavy pages
    python bolshoi_scraper.py --use_web --use_selenium --output "bolshoi_performances.json"
"""

import os
import sys
import json
import logging
import re
import time
from datetime import datetime
from bs4 import BeautifulSoup
from pymongo import MongoClient
import argparse

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import configuration and modules
from bolshoi_config import *
from bolshoi_web_fetcher import fetch_with_requests, fetch_with_selenium, fetch_with_retry, scrape_all_pages
from bolshoi_performance_details import scrape_performance_details

def read_in_chunks(file_object, chunk_size=8192):
    """Read a file in chunks to avoid memory issues with large files."""
    while True:
        data = file_object.read(chunk_size)
        if not data:
            break
        yield data

def get_mongodb_collection():
    """Connect to MongoDB and return the collection object."""
    try:
        client = MongoClient(MONGO_URI)
        db = client[DATABASE_NAME]
        return db[COLLECTION_NAME]
    except Exception as e:
        logger.error(f"Error connecting to MongoDB: {str(e)}")
        raise

def extract_ballet_performances(html_file):
    """
    Extract ballet performance data from the Bolshoi HTML file.
    
    Args:
        html_file (str): Path to the HTML file
        
    Returns:
        list: List of performance dictionaries
    """
    logger.info(f"Processing HTML file: {html_file}")
    
    # Check if file exists
    if not os.path.exists(html_file):
        logger.error(f"File not found: {html_file}")
        return []
    
    try:
        # Read the file in chunks to avoid memory issues
        html_content = ""
        with open(html_file, 'r', encoding='utf-8') as f:
            for chunk in read_in_chunks(f):
                html_content += chunk
        
        logger.info(f"HTML content loaded, length: {len(html_content)} characters")
        
        # Parse HTML with BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        logger.info("HTML parsed with BeautifulSoup")
        
        # Extract performances
        performances = []
        
        # Based on the structure of the extracted data, we need to parse the main content
        # which contains all the ballet performances
        
        # The first entry in our JSON contains all the ballet performances in its description
        # We need to parse this text to extract individual performances
        
        # Find all text that matches ballet performance patterns
        # Look for sections that start with "Ballet in" and end with age restriction or another pattern
        ballet_pattern = re.compile(r'Ballet\s+(?:in|by).*?(?:\d+\+|$)', re.DOTALL)
        ballet_sections = ballet_pattern.findall(html_content)
        
        # Use ballet titles from config
        ballet_titles = BALLET_TITLES
        
        # Extract sections around ballet titles
        for title in ballet_titles:
            title_pattern = re.compile(f"{title}.*?(?:\d+\+|$)", re.DOTALL)
            title_sections = title_pattern.findall(html_content)
            if title_sections:
                logger.info(f"Found section for ballet: {title}")
                ballet_sections.extend(title_sections)
        
        logger.info(f"Found {len(ballet_sections)} potential ballet sections")
        
        # Process each ballet section
        for idx, section in enumerate(ballet_sections):
            try:
                # First check if this is a section from the ballet titles list
                title = "Unknown Ballet"
                for ballet_title in ballet_titles:
                    if ballet_title in section:
                        title = ballet_title
                        break
                
                # If not found, try to extract from the pattern
                if title == "Unknown Ballet":
                    title_match = re.search(r'Ballet\s+(?:in|by).*?\n\s*(.*?)(?:\n|$)', section)
                    if title_match:
                        title = title_match.group(1).strip()
                
                # Extract composer/music
                composer_match = re.search(r'((?:to music by|by).*?)(?:\n|\d+\+|$)', section)
                composer = composer_match.group(1).strip() if composer_match else ""
                
                # Extract date if present
                date_match = re.search(r'(\d+\s+\w+\s+\d{4}\s+[-–]\s+\d+\s+\w+\s+\d{4}|\d+\s+[-–]\s+\d+\s+\w+\s+\d{4})', section)
                date = date_match.group(1).strip() if date_match else ""
                
                # Extract age restriction
                age_match = re.search(r'(\d+\+)', section)
                age_restriction = age_match.group(1) if age_match else ""
                
                # Extract ballet type
                type_match = re.search(r'(Ballet\s+(?:in|by).*?)(?:\n|$)', section)
                ballet_type = type_match.group(1).strip() if type_match else ""
                
                # Clean up HTML from extracted fields
                for field in ['title', 'composer', 'date', 'age_restriction', 'ballet_type']:
                    if locals()[field] and isinstance(locals()[field], str):
                        # Remove HTML tags and everything after them
                        locals()[field] = re.sub(r'<.*', '', locals()[field])
                        # Remove extra whitespace
                        locals()[field] = re.sub(r'\s+', ' ', locals()[field]).strip()
                
                # Create performance object
                performance = {
                    'title': title,
                    'composer': composer,
                    'date': date,
                    'age_restriction': age_restriction,
                    'ballet_type': ballet_type,
                    'venue': 'Bolshoi Theatre',
                    'source': 'Bolshoi Theatre Website',
                    'details_scraped': True,
                    'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                performances.append(performance)
                logger.info(f"Extracted performance {idx+1}: {title}")
                
            except Exception as e:
                logger.error(f"Error processing ballet section {idx+1}: {str(e)}")
                continue
        
        # If we couldn't extract performances using the pattern approach,
        # try to extract from the structured HTML
        if not performances:
            logger.info("Attempting to extract performances from structured HTML")
            
            # Look for elements that might contain performance information
            performance_elements = soup.find_all(['div', 'article'], class_=lambda c: c and any(term in c.lower() for term in ['performance', 'event', 'show']))
            
            for idx, element in enumerate(performance_elements):
                try:
                    # Extract title
                    title_elem = element.find(['h2', 'h3', 'h4', 'div', 'span'], class_=lambda c: c and any(term in c.lower() for term in ['title', 'name', 'heading']))
                    title = title_elem.text.strip() if title_elem else "Unknown Ballet"
                    
                    # Extract date
                    date_elem = element.find(class_=lambda c: c and any(term in c.lower() for term in ['date', 'time', 'when']))
                    date = date_elem.text.strip() if date_elem else ""
                    
                    # Create performance object
                    performance = {
                        'title': title,
                        'date': date,
                        'venue': 'Bolshoi Theatre',
                        'source': 'Bolshoi Theatre Website',
                        'details_scraped': True,
                        'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                    
                    performances.append(performance)
                    logger.info(f"Extracted performance {idx+1}: {title}")
                    
                except Exception as e:
                    logger.error(f"Error processing performance element {idx+1}: {str(e)}")
                    continue
        
        logger.info(f"Extracted {len(performances)} performances")
        return performances
        
    except Exception as e:
        logger.error(f"Error processing HTML file: {str(e)}")
        return []

def store_performances(collection, performances):
    """Store performances in MongoDB."""
    try:
        for performance in performances:
            # Use upsert to update existing entries or insert new ones
            collection.update_one(
                {'title': performance['title']},
                {'$set': performance},
                upsert=True
            )
        logger.info(f"Stored {len(performances)} performances in MongoDB")
        return True
    except Exception as e:
        logger.error(f"Error storing performances in MongoDB: {str(e)}")
        return False

def extract_ballet_performances_from_url(url=BASE_URL, use_selenium=False):
    """
    Extract ballet performance data directly from the Bolshoi Theatre website.
    
    Args:
        url (str): URL to scrape
        use_selenium (bool): Whether to use Selenium for JavaScript-heavy pages
        
    Returns:
        list: List of performance dictionaries
    """
    logger.info(f"Processing URL: {url}")
    
    try:
        # Fetch HTML content
        if use_selenium:
            html_content = fetch_with_selenium(url)
        else:
            html_content = fetch_with_requests(url)
        
        if not html_content:
            logger.error("Failed to fetch HTML content")
            return []
        
        logger.info(f"HTML content fetched, length: {len(html_content)} characters")
        
        # Parse HTML with BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        logger.info("HTML parsed with BeautifulSoup")
        
        # Extract performances using the same logic as extract_ballet_performances
        performances = []
        
        # Find all text that matches ballet performance patterns
        ballet_pattern = re.compile(r'Ballet\s+(?:in|by).*?(?:\d+\+|$)', re.DOTALL)
        ballet_sections = ballet_pattern.findall(html_content)
        
        # Use ballet titles from config
        ballet_titles = BALLET_TITLES
        
        # Extract sections around ballet titles
        for title in ballet_titles:
            title_pattern = re.compile(f"{title}.*?(?:\d+\+|$)", re.DOTALL)
            title_sections = title_pattern.findall(html_content)
            if title_sections:
                logger.info(f"Found section for ballet: {title}")
                ballet_sections.extend(title_sections)
        
        logger.info(f"Found {len(ballet_sections)} potential ballet sections")
        
        # Process each ballet section (same logic as in extract_ballet_performances)
        for idx, section in enumerate(ballet_sections):
            try:
                # First check if this is a section from the ballet titles list
                title = "Unknown Ballet"
                for ballet_title in ballet_titles:
                    if ballet_title in section:
                        title = ballet_title
                        break
                
                # If not found, try to extract from the pattern
                if title == "Unknown Ballet":
                    title_match = re.search(r'Ballet\s+(?:in|by).*?\n\s*(.*?)(?:\n|$)', section)
                    if title_match:
                        title = title_match.group(1).strip()
                
                # Extract composer/music
                composer_match = re.search(r'((?:to music by|by).*?)(?:\n|\d+\+|$)', section)
                composer = composer_match.group(1).strip() if composer_match else ""
                
                # Extract date if present
                date_match = re.search(r'(\d+\s+\w+\s+\d{4}\s+[-–]\s+\d+\s+\w+\s+\d{4}|\d+\s+[-–]\s+\d+\s+\w+\s+\d{4})', section)
                date = date_match.group(1).strip() if date_match else ""
                
                # Extract age restriction
                age_match = re.search(r'(\d+\+)', section)
                age_restriction = age_match.group(1) if age_match else ""
                
                # Extract ballet type
                type_match = re.search(r'(Ballet\s+(?:in|by).*?)(?:\n|$)', section)
                ballet_type = type_match.group(1).strip() if type_match else ""
                
                # Clean up HTML from extracted fields
                for field in ['title', 'composer', 'date', 'age_restriction', 'ballet_type']:
                    if locals()[field] and isinstance(locals()[field], str):
                        # Remove HTML tags and everything after them
                        locals()[field] = re.sub(r'<.*', '', locals()[field])
                        # Remove extra whitespace
                        locals()[field] = re.sub(r'\s+', ' ', locals()[field]).strip()
                
                # Create performance object
                performance = {
                    'title': title,
                    'composer': composer,
                    'date': date,
                    'age_restriction': age_restriction,
                    'ballet_type': ballet_type,
                    'venue': 'Bolshoi Theatre',
                    'source': 'Bolshoi Theatre Website',
                    'url': f"{BASE_URL}/performances/{title.lower().replace(' ', '-')}",
                    'details_scraped': False,
                    'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                performances.append(performance)
                logger.info(f"Extracted performance {idx+1}: {title}")
                
            except Exception as e:
                logger.error(f"Error processing ballet section {idx+1}: {str(e)}")
                continue
        
        # If we couldn't extract performances using the pattern approach,
        # try to extract from the structured HTML (same as in extract_ballet_performances)
        if not performances:
            logger.info("Attempting to extract performances from structured HTML")
            
            # Look for elements that might contain performance information
            performance_elements = soup.find_all(['div', 'article'], class_=lambda c: c and any(term in c.lower() for term in ['performance', 'event', 'show']))
            
            for idx, element in enumerate(performance_elements):
                try:
                    # Extract title
                    title_elem = element.find(['h2', 'h3', 'h4', 'div', 'span'], class_=lambda c: c and any(term in c.lower() for term in ['title', 'name', 'heading']))
                    title = title_elem.text.strip() if title_elem else "Unknown Ballet"
                    
                    # Extract date
                    date_elem = element.find(class_=lambda c: c and any(term in c.lower() for term in ['date', 'time', 'when']))
                    date = date_elem.text.strip() if date_elem else ""
                    
                    # Extract URL if available
                    url = ""
                    link_elem = element.find('a')
                    if link_elem and 'href' in link_elem.attrs:
                        url = link_elem['href']
                        if not url.startswith('http'):
                            url = f"https://www.bolshoi.ru{url}"
                    
                    # Create performance object
                    performance = {
                        'title': title,
                        'date': date,
                        'venue': 'Bolshoi Theatre',
                        'source': 'Bolshoi Theatre Website',
                        'url': url,
                        'details_scraped': False,
                        'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                    
                    performances.append(performance)
                    logger.info(f"Extracted performance {idx+1}: {title}")
                    
                except Exception as e:
                    logger.error(f"Error processing performance element {idx+1}: {str(e)}")
                    continue
        
        logger.info(f"Extracted {len(performances)} performances from URL")
        return performances
        
    except Exception as e:
        logger.error(f"Error processing URL: {str(e)}")
        return []

def scrape_all_performances(use_web=False, use_selenium=False, html_file=LOCAL_HTML_PATH, scrape_details=False):
    """
    Scrape all performances, either from a local file or from the web.
    
    Args:
        use_web (bool): Whether to scrape from the web
        use_selenium (bool): Whether to use Selenium for web scraping
        html_file (str): Path to the local HTML file
        scrape_details (bool): Whether to scrape detailed information for each performance
        
    Returns:
        list: List of performance dictionaries
    """
    performances = []
    
    if use_web:
        logger.info("Scraping performances from the web")
        
        # Scrape all pages
        html_contents = scrape_all_pages(BASE_URL, use_selenium)
        
        # Process each page
        for idx, html_content in enumerate(html_contents):
            logger.info(f"Processing page {idx+1}")
            
            # Create a temporary file to store the HTML content
            temp_file = f"temp_bolshoi_page_{idx}.html"
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # Extract performances from the temporary file
            page_performances = extract_ballet_performances(temp_file)
            performances.extend(page_performances)
            
            # Remove the temporary file
            os.remove(temp_file)
    else:
        logger.info("Scraping performances from local file")
        performances = extract_ballet_performances(html_file)
    
    # Scrape detailed information for each performance if requested
    if scrape_details:
        logger.info("Scraping detailed information for each performance")
        
        enriched_performances = []
        for idx, performance in enumerate(performances):
            logger.info(f"Scraping details for performance {idx+1}/{len(performances)}: {performance['title']}")
            
            # Scrape details
            enriched_performance = scrape_performance_details(performance, use_selenium)
            enriched_performances.append(enriched_performance)
            
            # Respect rate limiting
            time.sleep(REQUEST_DELAY)
        
        performances = enriched_performances
    
    return performances

def main():
    """Main function to process HTML files and store data in MongoDB."""
    parser = argparse.ArgumentParser(description='Scrape ballet performance data from Bolshoi Theatre')
    parser.add_argument('--html_file', help='Path to the HTML file to process (defaults to config value)', default=LOCAL_HTML_PATH)
    parser.add_argument('--url', help='URL to scrape instead of using a local file', default=BASE_URL)
    parser.add_argument('--use_web', help='Scrape directly from the web instead of using a local file', action='store_true')
    parser.add_argument('--use_selenium', help='Use Selenium for web scraping (for JavaScript-heavy pages)', action='store_true')
    parser.add_argument('--scrape_details', help='Scrape detailed information for each performance', action='store_true')
    parser.add_argument('--output', help='Path to save JSON output (optional)')
    parser.add_argument('--no-db', help='Skip storing in MongoDB', action='store_true')
    
    args = parser.parse_args()
    
    # Extract performances
    performances = scrape_all_performances(
        use_web=args.use_web,
        use_selenium=args.use_selenium,
        html_file=args.html_file,
        scrape_details=args.scrape_details
    )
    
    # Save to JSON if output file specified
    if args.output:
        try:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(performances, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved {len(performances)} performances to {args.output}")
        except Exception as e:
            logger.error(f"Error saving to JSON: {str(e)}")
    
    # Store in MongoDB if not skipped
    if not args.no_db:
        try:
            collection = get_mongodb_collection()
            store_performances(collection, performances)
        except Exception as e:
            logger.error(f"Failed to store performances in MongoDB: {str(e)}")
    else:
        logger.info("Skipping MongoDB storage (--no-db flag used)")

if __name__ == "__main__":
    main()
