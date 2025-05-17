#!/usr/bin/env python3
"""
Bolshoi Performance Details Scraper

This module handles scraping detailed information about ballet performances
from individual performance pages on the Bolshoi Theatre website.

Usage:
    from bolshoi_performance_details import scrape_performance_details

Example:
    performance = {
        'title': 'Swan Lake',
        'url': 'https://www.bolshoi.ru/en/performances/45/details/'
    }
    enriched_performance = scrape_performance_details(performance)
"""

import logging
import re
from bs4 import BeautifulSoup
from datetime import datetime

from bolshoi_web_fetcher import fetch_with_retry

# Configure logging
logger = logging.getLogger(__name__)

def clean_text(text):
    """Clean text by removing extra whitespace and normalizing."""
    if not text:
        return ""
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def extract_cast(soup):
    """Extract cast information from the performance page."""
    cast_info = {}
    
    # Look for cast sections
    cast_sections = soup.find_all(['div', 'section'], class_=lambda c: c and any(term in c.lower() for term in ['cast', 'performers', 'artists', 'credits']))
    
    for section in cast_sections:
        # Try to find role-performer pairs
        roles = []
        performers = []
        
        # Look for structured role-performer pairs
        role_elements = section.find_all(['dt', 'th', 'strong', 'b'])
        for role_elem in role_elements:
            # Find the corresponding performer element
            performer_elem = role_elem.find_next(['dd', 'td', 'span'])
            if performer_elem:
                roles.append(clean_text(role_elem.text))
                performers.append(clean_text(performer_elem.text))
        
        # If we found structured pairs, add them to cast_info
        if roles and performers:
            for i in range(min(len(roles), len(performers))):
                cast_info[roles[i]] = performers[i]
        else:
            # If no structured pairs found, just extract the text
            cast_text = clean_text(section.text)
            if cast_text:
                cast_info['full_cast'] = cast_text
    
    return cast_info

def extract_performance_dates(soup):
    """Extract performance dates from the page."""
    dates = []
    
    # Look for date elements
    date_elements = soup.find_all(['div', 'span', 'p'], class_=lambda c: c and any(term in c.lower() for term in ['date', 'when', 'schedule']))
    
    for date_elem in date_elements:
        # Look for date patterns
        date_text = date_elem.text
        
        # Pattern for dates like "25 May 2025" or "25 – 27 May 2025"
        date_matches = re.findall(r'\d{1,2}\s+[-–]?\s*\d{1,2}?\s+\w+\s+\d{4}', date_text)
        dates.extend(date_matches)
        
        # Pattern for dates like "May 25, 2025" or "May 25-27, 2025"
        date_matches2 = re.findall(r'\w+\s+\d{1,2}[-–]?\d{1,2}?,\s+\d{4}', date_text)
        dates.extend(date_matches2)
    
    return [clean_text(date) for date in dates]

def extract_description(soup):
    """Extract detailed description from the performance page."""
    # Look for description elements
    desc_elements = soup.find_all(['div', 'section', 'article'], class_=lambda c: c and any(term in c.lower() for term in ['description', 'about', 'synopsis', 'content']))
    
    descriptions = []
    for desc_elem in desc_elements:
        # Skip elements that are too short
        if len(desc_elem.text.strip()) < 50:
            continue
        
        # Skip elements that contain navigation or menus
        if desc_elem.find(['nav', 'menu']) or len(desc_elem.find_all('a')) > 5:
            continue
        
        descriptions.append(clean_text(desc_elem.text))
    
    # Return the longest description
    if descriptions:
        return max(descriptions, key=len)
    
    return ""

def extract_images(soup, base_url):
    """Extract high-resolution images from the performance page."""
    images = []
    
    # Look for image elements
    img_elements = soup.find_all('img')
    
    for img in img_elements:
        if 'src' in img.attrs:
            img_url = img['src']
            
            # Skip small icons and logos
            if any(term in img_url.lower() for term in ['icon', 'logo', 'button']):
                continue
                
            # Make relative URLs absolute
            if not img_url.startswith('http'):
                img_url = f"{base_url.rstrip('/')}/{img_url.lstrip('/')}"
            
            # Look for high-resolution versions
            # Often sites use patterns like image_small.jpg vs image_large.jpg
            img_url = img_url.replace('_small', '_large').replace('_thumb', '_full')
            
            images.append(img_url)
    
    return images

def scrape_performance_details(performance, use_selenium=False):
    """
    Scrape additional details from a performance's detail page.
    
    Args:
        performance (dict): Performance data with URL
        use_selenium (bool): Whether to use Selenium for JavaScript-heavy pages
        
    Returns:
        dict: Updated performance data with details
    """
    if not performance.get('url'):
        logger.warning(f"No URL provided for performance: {performance.get('title', 'Unknown')}")
        return performance
        
    url = performance['url']
    logger.info(f"Scraping details from: {url}")
    
    html_content = fetch_with_retry(url, use_selenium)
    if not html_content:
        logger.error(f"Failed to fetch content from {url}")
        return performance
        
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract detailed description
        description = extract_description(soup)
        if description:
            performance['detailed_description'] = description
            
        # Extract cast information
        cast_info = extract_cast(soup)
        if cast_info:
            performance['cast'] = cast_info
            
        # Extract performance dates
        dates = extract_performance_dates(soup)
        if dates:
            performance['performance_dates'] = dates
            
        # Extract high-resolution images
        images = extract_images(soup, url)
        if images:
            performance['images'] = images
            
        # Extract duration if available
        duration_elem = soup.find(string=re.compile(r'duration|running time', re.I))
        if duration_elem:
            parent = duration_elem.parent
            duration_text = clean_text(parent.text)
            performance['duration'] = duration_text
            
        # Mark as having details scraped
        performance['details_scraped'] = True
        performance['details_last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
    except Exception as e:
        logger.error(f"Error scraping details from {url}: {str(e)}")
        
    return performance

if __name__ == "__main__":
    # Configure logging for standalone testing
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Test with a sample performance
    test_performance = {
        'title': 'Swan Lake',
        'url': 'https://www.bolshoi.ru/en/performances/45/details/'
    }
    
    print(f"Testing detail scraper with performance: {test_performance['title']}")
    enriched = scrape_performance_details(test_performance, use_selenium=True)
    
    print("Enriched performance data:")
    for key, value in enriched.items():
        if key != 'detailed_description':
            print(f"{key}: {value}")
        else:
            print(f"{key}: {value[:100]}... (truncated)")
