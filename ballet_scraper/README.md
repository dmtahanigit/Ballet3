# Ballet Performance Scraper

A Python scraper that collects ballet performance information from the Paris Opera website and stores it in MongoDB.

## Features

- Scrapes performance details including title, venue, dates, descriptions, and video links
- Stores data in MongoDB for easy access and querying
- Automatically handles cookie consent popups
- Includes rate limiting to avoid overwhelming the website
- Runs on a weekly schedule to keep data up to date
- Comprehensive error handling and logging

## Prerequisites

- Python 3.9 or higher
- Chrome browser installed
- ChromeDriver installed and in your system PATH
- MongoDB account and connection string

## Installation

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

The `config.py` file contains all configuration settings:

- MongoDB connection details
- Base URL for scraping
- Rate limiting settings
- Update schedule interval

## Usage

Run the scraper:
```bash
python main.py
```

The scraper will:
1. Run an initial scrape immediately
2. Schedule subsequent runs every 7 days
3. Log all activities to the console

## Data Structure

Each performance is stored in MongoDB with the following structure:

```json
{
    "title": "Performance Title",
    "url": "https://www.operadeparis.fr/...",
    "thumbnail": "https://...",
    "venue": "Venue Name",
    "date": "Performance date range",
    "description": "Full description (if available)",
    "video_links": ["https://youtube.com/..."],
    "details_scraped": true/false,
    "last_updated": "2025-04-28 20:30:00"
}
```

The scraper uses a two-phase approach:
1. Core data (guaranteed):
   - Title
   - URL
   - Thumbnail
   - Venue
   - Date
   These are always available from the main listing page.

2. Additional details (best effort):
   - Description
   - Video links
   These are attempted to be scraped from individual performance pages.

## Error Handling

- The scraper uses a resilient two-phase approach:
  1. Core information is always saved, even if additional details fail
  2. Failed detail scrapes are marked with details_scraped=false
- Random delays between requests prevent rate limiting
- Comprehensive logging for debugging
- Simplified retry strategy focuses on reliability

## Logging

Logs include:
- Scraping start/completion
- Individual performance processing
- Error messages
- Cookie consent status
- Scheduling information

## Maintenance

- Check logs regularly for any persistent errors
- Update ChromeDriver as needed
- Monitor MongoDB storage usage
- Review rate limiting if needed
