#!/usr/bin/env python3
"""
Bolshoi HTML Processor

This script processes the downloaded Bolshoi Theatre HTML files to extract performance data
and save it in a structured format that can be used by the scraper.

Usage:
    python bolshoi_html_processor.py [input_file] [output_file]

Example:
    python bolshoi_html_processor.py "../Bolshoi HTML TEST/Bolshoi Theatre • Season.html" "bolshoi_performances.json"
"""

import os
import sys
import json
import logging
import re
from bs4 import BeautifulSoup
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def read_in_chunks(file_object, chunk_size=8192):
    """Read a file in chunks to avoid memory issues with large files."""
    while True:
        data = file_object.read(chunk_size)
        if not data:
            break
        yield data

def extract_performance_data(html_file):
    """
    Extract performance data from the Bolshoi HTML file.
    
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
    
    # Get file size
    file_size = os.path.getsize(html_file)
    logger.info(f"File size: {file_size / (1024 * 1024):.2f} MB")
    
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
        
        # Look for performance cards/items
        # Based on the file structure, we'll try different selectors
        
        # Try different approaches to find performance elements
        
        # Look for elements with specific attributes that might indicate performances
        performance_elements = []
        
        # First attempt: Look for elements with class containing 'performance' or 'event'
        elements1 = soup.find_all(class_=lambda c: c and any(term in c.lower() for term in ['performance', 'event', 'show', 'production']))
        logger.info(f"Found {len(elements1)} elements with performance-related classes")
        performance_elements.extend(elements1)
        
        # Second attempt: Look for elements that might contain performance data
        elements2 = soup.find_all('div', class_='event-card')
        logger.info(f"Found {len(elements2)} elements with class 'event-card'")
        performance_elements.extend(elements2)
        
        # Third attempt: Look for list items that might be performances
        elements3 = soup.find_all('li', class_=lambda c: c and 'item' in c.lower())
        logger.info(f"Found {len(elements3)} list items that might be performances")
        performance_elements.extend(elements3)
        
        # Fourth attempt: Look for any div with an image and a heading
        for div in soup.find_all('div'):
            if div.find('img') and div.find(['h1', 'h2', 'h3', 'h4']):
                performance_elements.append(div)
        logger.info(f"Found {len(performance_elements) - len(elements1) - len(elements2) - len(elements3)} divs with images and headings")
        
        # Fifth attempt: Look for any article elements
        elements5 = soup.find_all('article')
        logger.info(f"Found {len(elements5)} article elements")
        performance_elements.extend(elements5)
        
        # Sixth attempt: Look for any div with a link and a date pattern
        date_pattern = re.compile(r'\d{1,2}[./-]\d{1,2}[./-]\d{2,4}')
        for div in soup.find_all('div'):
            if div.find('a') and date_pattern.search(div.text):
                if div not in performance_elements:
                    performance_elements.append(div)
        
        # Seventh attempt: Look for elements with specific Russian ballet-related terms
        ballet_terms = ['балет', 'спектакль', 'премьера', 'опера', 'концерт']
        for div in soup.find_all(['div', 'section', 'article']):
            if any(term in div.text.lower() for term in ballet_terms):
                if div not in performance_elements and len(div.text) < 2000:  # Avoid very large containers
                    performance_elements.append(div)
        
        # Eighth attempt: Look for elements with specific date formats common in Russian sites
        russian_date_pattern = re.compile(r'\d{1,2}\s+[а-яА-Я]+\s+\d{4}')  # e.g., "12 мая 2025"
        for div in soup.find_all('div'):
            if russian_date_pattern.search(div.text) and div not in performance_elements:
                performance_elements.append(div)
                
        logger.info(f"Total performance elements found: {len(performance_elements)}")
        
        # Process each potential performance element
        for idx, element in enumerate(performance_elements[:30]):  # Limit to first 30 for initial analysis
            try:
                # Extract basic information - try multiple approaches for title
                title = "Unknown Title"
                
                # First try to find elements with title-related classes
                title_elem = element.find(['h2', 'h3', 'h4', 'div', 'span'], class_=lambda c: c and any(term in c.lower() for term in ['title', 'name', 'heading']))
                if title_elem:
                    title = title_elem.text.strip()
                else:
                    # Try to find any heading element
                    heading = element.find(['h1', 'h2', 'h3', 'h4'])
                    if heading:
                        title = heading.text.strip()
                    else:
                        # Try to find strong or b elements that might contain titles
                        bold = element.find(['strong', 'b'])
                        if bold:
                            title = bold.text.strip()
                        else:
                            # Try to find the first significant text node
                            for text in element.stripped_strings:
                                if len(text) > 5 and not text.isspace():  # Avoid very short or whitespace-only strings
                                    title = text
                                    break
                
                # Extract URL if available
                url = ""
                link_elem = element.find('a')
                if link_elem and 'href' in link_elem.attrs:
                    url = link_elem['href']
                    if not url.startswith('http'):
                        url = f"https://www.bolshoi.ru{url}"
                
                # Extract image/thumbnail if available
                thumbnail = ""
                img_elem = element.find('img')
                if img_elem and 'src' in img_elem.attrs:
                    thumbnail = img_elem['src']
                    if not thumbnail.startswith('http'):
                        thumbnail = f"https://www.bolshoi.ru{thumbnail}"
                
                # Extract date information
                date_elem = element.find(class_=lambda c: c and any(term in c.lower() for term in ['date', 'time', 'when']))
                date_text = date_elem.text.strip() if date_elem else ""
                
                # Extract venue information
                venue_elem = element.find(class_=lambda c: c and any(term in c.lower() for term in ['venue', 'location', 'place']))
                venue = venue_elem.text.strip() if venue_elem else "Bolshoi Theatre"
                
                # Extract description if available
                desc_elem = element.find(class_=lambda c: c and any(term in c.lower() for term in ['description', 'summary', 'content']))
                description = desc_elem.text.strip() if desc_elem else ""
                
                # Create performance object
                performance = {
                    'title': title,
                    'url': url,
                    'thumbnail': thumbnail,
                    'date': date_text,
                    'venue': venue,
                    'description': description,
                    'source_element': str(element)[:500] + '...' if len(str(element)) > 500 else str(element)  # Store truncated source for analysis
                }
                
                performances.append(performance)
                logger.info(f"Extracted performance {idx+1}: {title}")
                
            except Exception as e:
                logger.error(f"Error processing element {idx+1}: {str(e)}")
                continue
        
        logger.info(f"Extracted {len(performances)} performances")
        return performances
        
    except Exception as e:
        logger.error(f"Error processing HTML file: {str(e)}")
        return []

def save_to_json(performances, output_file):
    """Save performances to a JSON file."""
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(performances, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved {len(performances)} performances to {output_file}")
        return True
    except Exception as e:
        logger.error(f"Error saving to JSON: {str(e)}")
        return False

def analyze_html_structure(html_file):
    """Analyze the HTML structure to identify performance elements."""
    logger.info(f"Analyzing HTML structure: {html_file}")
    
    try:
        # Read a sample of the file (first 500KB) to analyze structure
        with open(html_file, 'r', encoding='utf-8') as f:
            sample = f.read(500 * 1024)  # Read first 500KB
        
        soup = BeautifulSoup(sample, 'html.parser')
        
        # Find all div elements with class attributes
        elements_with_class = soup.find_all(lambda tag: tag.name == 'div' and tag.has_attr('class'))
        
        # Count occurrences of different class names
        class_counts = {}
        for elem in elements_with_class:
            for class_name in elem.get('class', []):
                class_counts[class_name] = class_counts.get(class_name, 0) + 1
        
        # Sort by frequency
        sorted_classes = sorted(class_counts.items(), key=lambda x: x[1], reverse=True)
        
        # Log the most common classes
        logger.info("Most common CSS classes:")
        for class_name, count in sorted_classes[:20]:
            logger.info(f"  {class_name}: {count} occurrences")
        
        # Look for potential performance containers
        potential_containers = []
        for class_name, count in sorted_classes:
            if 5 <= count <= 50:  # Reasonable range for performance items
                # Check if class name suggests it's a performance container
                if any(term in class_name.lower() for term in ['item', 'card', 'event', 'performance', 'show']):
                    # Get a sample element
                    sample_elem = soup.find('div', class_=class_name)
                    if sample_elem:
                        potential_containers.append({
                            'class_name': class_name,
                            'count': count,
                            'has_title': bool(sample_elem.find(['h2', 'h3', 'h4'])),
                            'has_link': bool(sample_elem.find('a')),
                            'has_image': bool(sample_elem.find('img')),
                            'sample': str(sample_elem)[:200] + '...' if len(str(sample_elem)) > 200 else str(sample_elem)
                        })
        
        logger.info(f"Found {len(potential_containers)} potential performance containers")
        for container in potential_containers:
            logger.info(f"  {container['class_name']}: {container['count']} occurrences, has_title={container['has_title']}, has_link={container['has_link']}, has_image={container['has_image']}")
        
        return potential_containers
        
    except Exception as e:
        logger.error(f"Error analyzing HTML structure: {str(e)}")
        return []

def main():
    """Main function to process HTML files."""
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} [input_file] [output_file]")
        print(f"Example: {sys.argv[0]} '../Bolshoi HTML TEST/Bolshoi Theatre • Season.html' 'bolshoi_performances.json'")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    # First analyze the HTML structure
    logger.info("Step 1: Analyzing HTML structure")
    potential_containers = analyze_html_structure(input_file)
    
    # Then extract performance data
    logger.info("Step 2: Extracting performance data")
    performances = extract_performance_data(input_file)
    
    # Save the results
    logger.info("Step 3: Saving results")
    if save_to_json(performances, output_file):
        logger.info("Processing completed successfully")
    else:
        logger.error("Failed to save results")

if __name__ == "__main__":
    main()
