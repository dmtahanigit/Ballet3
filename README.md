# Ballet World

A comprehensive platform for ballet enthusiasts to discover performances from major ballet companies around the world.

## Project Overview

Ballet World is a data aggregation and API service that collects information about ballet performances from various ballet companies' websites. The project includes:

1. **Scrapers** for different ballet companies:
   - Paris Opera Ballet
   - Bolshoi Ballet
   - Boston Ballet
   - (More to be added in the future)

2. **API Server** to provide access to the collected data

3. **Web Interface** (in the PageTests directory) for displaying the data

## Project Structure

```
Ballet World/
├── api/                      # API server
│   ├── __init__.py
│   ├── server.py             # Flask API implementation
│   └── tests/                # API tests
│
├── scrapers/                 # Scrapers for different ballet companies
│   ├── common/               # Shared utilities
│   │   ├── __init__.py
│   │   ├── db.py             # Database utilities
│   │   └── utils.py          # Common scraping utilities
│   │
│   ├── paris_opera_ballet/   # Paris Opera Ballet scraper
│   │   ├── __init__.py
│   │   ├── config.py         # Configuration
│   │   ├── scraper.py        # Main scraper implementation
│   │   └── tests/            # Tests
│   │
│   ├── bolshoi_ballet/       # Bolshoi Ballet scraper
│   │   ├── __init__.py
│   │   ├── config.py         # Configuration
│   │   ├── scraper.py        # Main scraper implementation
│   │   └── tests/            # Tests
│   │
│   └── boston_ballet/        # Boston Ballet scraper
│       ├── __init__.py
│       ├── config.py         # Configuration
│       ├── scraper.py        # Main scraper implementation
│       └── tests/            # Tests
│
├── PageTests/                # Web interface for testing and display
│
├── .env                      # Environment variables (not in repo)
├── .gitignore                # Git ignore file
├── requirements.txt          # Python dependencies
├── run.py                    # Main entry point
└── README.md                 # This file
```

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- MongoDB (local or remote)
- Chrome/Chromium (for Selenium-based scraping)
- ChromeDriver (for Selenium-based scraping)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/ballet-world.git
   cd ballet-world
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file with the following variables:
   ```
   MONGODB_URI=mongodb://localhost:27017/
   DATABASE_NAME=ballet_world
   COLLECTION_NAME=paris_opera_ballet
   BOLSHOI_COLLECTION_NAME=bolshoi_ballet
   BOSTON_COLLECTION_NAME=boston_ballet
   PORT=5000
   DEBUG=True
   ```

### Running the Application

The application can be run in several modes using the `run.py` script:

1. Run the Paris Opera Ballet scraper:
   ```bash
   python run.py pob
   ```

2. Run the Bolshoi Ballet scraper:
   ```bash
   # From local HTML file
   python run.py bolshoi
   
   # From the web
   python run.py bolshoi --web
   
   # Using Selenium
   python run.py bolshoi --web --selenium
   ```

3. Run the Boston Ballet scraper:
   ```bash
   python run.py boston
   ```

4. Run the API server:
   ```bash
   python run.py api
   ```

5. Run everything:
   ```bash
   python run.py all
   ```

For more options, run:
```bash
python run.py --help
```

## API Documentation

The API provides access to ballet performance data from various companies.

### Endpoints

- `GET /api/health` - Health check
- `GET /api/companies` - List of available ballet companies
- `GET /api/performances` - Get performances from all companies
- `GET /api/performances/{company_id}` - Get performances for a specific company
- `GET /api/performances/{company_id}/{performance_id}` - Get a specific performance
- `GET /api/search?q={query}` - Search performances across all companies

### Example Requests

```bash
# Get all performances
curl http://localhost:5000/api/performances

# Get Paris Opera Ballet performances
curl http://localhost:5000/api/performances/paris_opera_ballet

# Search for "Swan Lake"
curl http://localhost:5000/api/search?q=Swan%20Lake
```

## Development

### Adding a New Ballet Company

To add a new ballet company:

1. Create a new directory under `scrapers/` for the company
2. Create the following files:
   - `__init__.py`
   - `config.py` - Configuration settings
   - `scraper.py` - Scraper implementation
3. Update the API server to include the new company
4. Update the main `run.py` script to include the new scraper

### Running Tests

```bash
# Run all tests
pytest

# Run specific tests
pytest scrapers/paris_opera_ballet/tests/
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- Paris Opera Ballet - https://www.operadeparis.fr/
- Bolshoi Theatre - https://www.bolshoi.ru/
- Boston Ballet - https://www.bostonballet.org/
