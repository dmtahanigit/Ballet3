# MongoDB Configuration
MONGO_URI = "mongodb+srv://dineshmahtani:Dm4164651096*@cluster0ballet3.rq9aanh.mongodb.net/"
DATABASE_NAME = "ballet3"
COLLECTION_NAME = "paris_opera_ballet"

# Scraping Configuration
BASE_URL = "https://www.operadeparis.fr/en/programme/season-25-26/shows-ballet"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# Selenium Configuration
IMPLICIT_WAIT = 10  # seconds
PAGE_LOAD_TIMEOUT = 30  # seconds

# Update Schedule
UPDATE_INTERVAL = 7  # days

# Rate Limiting
REQUEST_DELAY = 2  # seconds between requests
