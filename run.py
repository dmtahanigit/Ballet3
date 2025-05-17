#!/usr/bin/env python3
"""
Main entry point for the Ballet World application.

This script provides a command-line interface to run the scrapers and API server.
"""

import os
import sys
import argparse
import logging
import time
import threading
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def run_paris_opera_ballet_scraper(args):
    """Run the Paris Opera Ballet scraper."""
    try:
        from scrapers.paris_opera_ballet.scraper import main_scrape, print_stored_data
        
        logger.info("Running Paris Opera Ballet scraper")
        success = main_scrape()
        
        if args.print_data:
            print_stored_data()
        
        return success
    except Exception as e:
        logger.error(f"Error running Paris Opera Ballet scraper: {str(e)}")
        return False

def run_bolshoi_ballet_scraper(args):
    """Run the Bolshoi Ballet scraper."""
    try:
        from scrapers.bolshoi_ballet.scraper import main_scrape, print_stored_data
        
        logger.info("Running Bolshoi Ballet scraper")
        success = main_scrape(
            use_web=args.web,
            use_selenium=args.selenium,
            html_file=args.file,
            scrape_details=not args.no_details
        )
        
        if args.print_data:
            print_stored_data()
        
        return success
    except Exception as e:
        logger.error(f"Error running Bolshoi Ballet scraper: {str(e)}")
        return False

def run_boston_ballet_scraper(args):
    """Run the Boston Ballet scraper."""
    try:
        from scrapers.boston_ballet.scraper import main_scrape, print_stored_data
        
        logger.info("Running Boston Ballet scraper")
        success = main_scrape(
            use_selenium=True,
            scrape_details=not args.no_details
        )
        
        if args.print_data:
            print_stored_data()
        
        return success
    except Exception as e:
        logger.error(f"Error running Boston Ballet scraper: {str(e)}")
        return False

def run_api_server(args):
    """Run the API server."""
    try:
        from api.server import main
        
        logger.info("Running API server")
        main()
        
        return True
    except Exception as e:
        logger.error(f"Error running API server: {str(e)}")
        return False

def run_all(args):
    """Run all components."""
    # Run scrapers in separate threads
    scraper_threads = []
    
    if not args.no_pob:
        pob_thread = threading.Thread(
            target=run_paris_opera_ballet_scraper,
            args=(args,),
            name="POB-Scraper"
        )
        scraper_threads.append(pob_thread)
    
    if not args.no_bolshoi:
        bolshoi_thread = threading.Thread(
            target=run_bolshoi_ballet_scraper,
            args=(args,),
            name="Bolshoi-Scraper"
        )
        scraper_threads.append(bolshoi_thread)
    
    if not args.no_boston:
        boston_thread = threading.Thread(
            target=run_boston_ballet_scraper,
            args=(args,),
            name="Boston-Scraper"
        )
        scraper_threads.append(boston_thread)
    
    # Start scraper threads
    for thread in scraper_threads:
        thread.start()
    
    # Wait for scrapers to finish
    for thread in scraper_threads:
        thread.join()
    
    # Run API server (this will block)
    if not args.no_api:
        run_api_server(args)
    
    return True

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Ballet World Application')
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Paris Opera Ballet scraper command
    pob_parser = subparsers.add_parser('pob', help='Run Paris Opera Ballet scraper')
    pob_parser.add_argument('--print-data', action='store_true', help='Print stored data after scraping')
    
    # Bolshoi Ballet scraper command
    bolshoi_parser = subparsers.add_parser('bolshoi', help='Run Bolshoi Ballet scraper')
    bolshoi_parser.add_argument('--web', action='store_true', help='Scrape from the web instead of local file')
    bolshoi_parser.add_argument('--selenium', action='store_true', help='Use Selenium for web scraping')
    bolshoi_parser.add_argument('--file', type=str, help='Path to local HTML file')
    bolshoi_parser.add_argument('--no-details', action='store_true', help='Skip scraping individual performance details')
    bolshoi_parser.add_argument('--print-data', action='store_true', help='Print stored data after scraping')
    
    # API server command
    api_parser = subparsers.add_parser('api', help='Run API server')
    
    # Boston Ballet scraper command
    boston_parser = subparsers.add_parser('boston', help='Run Boston Ballet scraper')
    boston_parser.add_argument('--no-details', action='store_true', help='Skip scraping individual performance details')
    boston_parser.add_argument('--print-data', action='store_true', help='Print stored data after scraping')
    
    # All command (run everything)
    all_parser = subparsers.add_parser('all', help='Run all components')
    all_parser.add_argument('--no-pob', action='store_true', help='Skip Paris Opera Ballet scraper')
    all_parser.add_argument('--no-bolshoi', action='store_true', help='Skip Bolshoi Ballet scraper')
    all_parser.add_argument('--no-boston', action='store_true', help='Skip Boston Ballet scraper')
    all_parser.add_argument('--no-api', action='store_true', help='Skip API server')
    all_parser.add_argument('--web', action='store_true', help='Scrape from the web instead of local file (Bolshoi)')
    all_parser.add_argument('--selenium', action='store_true', help='Use Selenium for web scraping (Bolshoi)')
    all_parser.add_argument('--file', type=str, help='Path to local HTML file (Bolshoi)')
    all_parser.add_argument('--no-details', action='store_true', help='Skip scraping individual performance details')
    all_parser.add_argument('--print-data', action='store_true', help='Print stored data after scraping')
    
    args = parser.parse_args()
    
    if args.command == 'pob':
        success = run_paris_opera_ballet_scraper(args)
    elif args.command == 'bolshoi':
        success = run_bolshoi_ballet_scraper(args)
    elif args.command == 'boston':
        success = run_boston_ballet_scraper(args)
    elif args.command == 'api':
        success = run_api_server(args)
    elif args.command == 'all':
        success = run_all(args)
    else:
        parser.print_help()
        return 1
    
    return 0 if success else 1

if __name__ == '__main__':
    sys.exit(main())
