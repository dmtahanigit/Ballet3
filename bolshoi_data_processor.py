#!/usr/bin/env python3
"""
Bolshoi Data Processor

This script processes the extracted Bolshoi Theatre performance data to clean up HTML artifacts
and prepare it for integration with the main ballet database.

Usage:
    python bolshoi_data_processor.py [input_file] [output_file]

Example:
    python bolshoi_data_processor.py "bolshoi_performances_final.json" "bolshoi_performances_clean.json"
"""

import os
import sys
import json
import logging
import re
from datetime import datetime
import argparse

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def clean_html_content(text):
    """Clean HTML content from text."""
    if not text or not isinstance(text, str):
        return text
    
    # Remove HTML tags and everything after them
    text = re.sub(r'<.*', '', text)
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def process_performance_data(input_file, output_file):
    """
    Process and clean Bolshoi performance data.
    
    Args:
        input_file (str): Path to the input JSON file
        output_file (str): Path to save the cleaned JSON output
    """
    logger.info(f"Processing performance data from: {input_file}")
    
    # Check if file exists
    if not os.path.exists(input_file):
        logger.error(f"File not found: {input_file}")
        return False
    
    try:
        # Load the JSON data
        with open(input_file, 'r', encoding='utf-8') as f:
            performances = json.load(f)
        
        logger.info(f"Loaded {len(performances)} performances from {input_file}")
        
        # Process each performance
        cleaned_performances = []
        unique_titles = set()
        
        for idx, performance in enumerate(performances):
            try:
                # Clean all text fields
                cleaned_performance = {}
                for key, value in performance.items():
                    if isinstance(value, str):
                        cleaned_performance[key] = clean_html_content(value)
                    else:
                        cleaned_performance[key] = value
                
                # Fix specific issues
                if cleaned_performance.get('composer') and 'bycawirsoq_420x900_p.jpg' in cleaned_performance['composer']:
                    if 'Marco Spada' in cleaned_performance['title']:
                        cleaned_performance['composer'] = 'Daniel-François-Esprit Auber'
                
                # Add missing composers based on title
                composer_map = {
                    'Swan Lake': 'Pyotr Tchaikovsky',
                    'The Sleeping Beauty': 'Pyotr Tchaikovsky',
                    'The Nutcracker': 'Pyotr Tchaikovsky',
                    'Don Quixote': 'Ludwig Minkus',
                    'La Bayadère': 'Ludwig Minkus',
                    'Raymonda': 'Alexander Glazunov',
                    'Romeo and Juliet': 'Sergei Prokofiev',
                    'Spartacus': 'Aram Khachaturyan',
                    'The Flames of Paris': 'Boris Asafiev',
                    'Giselle': 'Adolphe Adam',
                    'La Sylphide': 'Herman Severin Levenskiold',
                    'Coppelia': 'Leo Delibes',
                    'Carmen Suite': 'Georges Bizet–Rodion Shchedrin',
                    'The Bright Stream': 'Dmitry Shostakovich',
                    'The Seagull': 'Ilya Demutsky',
                    'The Tempest': 'Yuri Krasavin',
                    'Dancemania': 'Yuri Krasavin',
                    'Cipollino': 'Karen Khachaturyan',
                    'A Legend of Love': 'Arif Melikov'
                }
                
                if not cleaned_performance.get('composer') and cleaned_performance['title'] in composer_map:
                    cleaned_performance['composer'] = composer_map[cleaned_performance['title']]
                
                # Extract composer from ballet_type if not present
                if not cleaned_performance.get('composer') and 'to music by' in cleaned_performance.get('ballet_type', ''):
                    composer_match = re.search(r'to music by\s+(.*?)(?:\s+\d+\+|$)', cleaned_performance['ballet_type'])
                    if composer_match:
                        cleaned_performance['composer'] = composer_match.group(1).strip()
                
                # Skip duplicates based on title
                if cleaned_performance['title'] in unique_titles:
                    continue
                
                unique_titles.add(cleaned_performance['title'])
                cleaned_performances.append(cleaned_performance)
                logger.info(f"Processed performance {idx+1}: {cleaned_performance['title']}")
                
            except Exception as e:
                logger.error(f"Error processing performance {idx+1}: {str(e)}")
                continue
        
        # Save the cleaned data
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(cleaned_performances, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved {len(cleaned_performances)} cleaned performances to {output_file}")
        return True
        
    except Exception as e:
        logger.error(f"Error processing performance data: {str(e)}")
        return False

def main():
    """Main function to process performance data."""
    parser = argparse.ArgumentParser(description='Process and clean Bolshoi performance data')
    parser.add_argument('input_file', help='Path to the input JSON file')
    parser.add_argument('output_file', help='Path to save the cleaned JSON output')
    
    args = parser.parse_args()
    
    # Process the data
    if process_performance_data(args.input_file, args.output_file):
        logger.info("Processing completed successfully")
    else:
        logger.error("Failed to process performance data")

if __name__ == "__main__":
    main()
