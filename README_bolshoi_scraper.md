# Bolshoi Theatre Ballet Scraper

This module provides tools for scraping ballet performance data from the Bolshoi Theatre website. It can work with both locally saved HTML files and by directly scraping the Bolshoi website.

## Features

- Extract ballet performance data from local HTML files
- Scrape directly from the Bolshoi Theatre website
- Support for JavaScript-heavy pages using Selenium
- Detailed performance information scraping
- MongoDB integration for data storage
- JSON export functionality
- Comprehensive error handling and logging
- Rate limiting to avoid overloading the website

## Installation

1. Install the required dependencies:

```bash
pip install -r requirements.txt
```

2. Make sure you have Chrome installed if you plan to use Selenium for web scraping.

## Usage

### Command Line Interface

The scraper can be run from the command line with various options:

```bash
python bolshoi_scraper.py [options]
```

Options:
- `--html_file PATH`: Path to the HTML file to process (defaults to config value)
- `--url URL`: URL to scrape instead of using a local file
- `--use_web`: Scrape directly from the web instead of using a local file
- `--use_selenium`: Use Selenium for web scraping (for JavaScript-heavy pages)
- `--scrape_details`: Scrape detailed information for each performance
- `--output PATH`: Path to save JSON output (optional)
- `--no-db`: Skip storing in MongoDB

### Using the Shell Script

For convenience, a shell script is provided to run the scraper with different options:

```bash
./run_bolshoi_scraper.sh [options]
```

Options:
- `-w, --web`: Scrape directly from the web instead of using a local file
- `-s, --selenium`: Use Selenium for web scraping (for JavaScript-heavy pages)
- `-d, --details`: Scrape detailed information for each performance
- `-o, --output FILE`: Path to save JSON output (default: bolshoi_performances_latest.json)
- `-f, --file FILE`: Path to the HTML file to process
- `--no-db`: Skip storing in MongoDB
- `-h, --help`: Show help message

Examples:
```bash
# Scrape from web with Selenium and details
./run_bolshoi_scraper.sh -w -s -d -o bolshoi_performances.json

# Process a local file
./run_bolshoi_scraper.sh -f local_file.html -o output.json
```

### Python API

You can also use the scraper as a Python module:

```python
from bolshoi_scraper import scrape_all_performances

# Scrape from a local file
performances = scrape_all_performances(html_file="path/to/file.html")

# Scrape from the web
performances = scrape_all_performances(use_web=True, use_selenium=True, scrape_details=True)

# Process the performances
for performance in performances:
    print(f"Title: {performance['title']}")
    print(f"Date: {performance['date']}")
    print(f"Composer: {performance.get('composer', 'Unknown')}")
    print("---")
```

## Module Structure

- `bolshoi_scraper.py`: Main scraper module
- `bolshoi_web_fetcher.py`: Web fetching functionality
- `bolshoi_performance_details.py`: Detailed performance information scraping
- `bolshoi_config.py`: Configuration settings
- `bolshoi_html_processor.py`: HTML processing utilities

## Configuration

The scraper can be configured by modifying the `bolshoi_config.py` file:

- MongoDB connection settings
- Base URL for the Bolshoi Theatre website
- HTTP headers for web requests
- Selenium configuration
- Rate limiting settings
- Ballet titles for pattern matching

## Data Format

The scraper extracts the following information for each performance:

- Title
- Composer/Music
- Performance dates
- Age restriction
- Ballet type (e.g., "Ballet in three acts")
- Venue
- Source
- URL (for web scraping)
- Detailed description (when using `--scrape_details`)
- Cast information (when using `--scrape_details`)
- Images (when using `--scrape_details`)
- Duration (when using `--scrape_details`)

## Error Handling

The scraper includes comprehensive error handling and logging:

- Connection errors are logged and retried
- Parsing errors are caught and reported
- Rate limiting is respected to avoid overloading the website
- Temporary files are cleaned up after use

## License

This project is licensed under the MIT License - see the LICENSE file for details.
