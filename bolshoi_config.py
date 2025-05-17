# MongoDB Configuration
MONGO_URI = "mongodb+srv://dineshmahtani:Dm4164651096*@cluster0ballet3.rq9aanh.mongodb.net/"
DATABASE_NAME = "ballet3"
COLLECTION_NAME = "bolshoi_ballet"

# Scraping Configuration
BASE_URL = "https://www.bolshoi.ru/en/season"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9,ru;q=0.8",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
}

# Selenium Configuration
IMPLICIT_WAIT = 15  # seconds
PAGE_LOAD_TIMEOUT = 45  # seconds

# Update Schedule
UPDATE_INTERVAL = 7  # days

# Rate Limiting
REQUEST_DELAY = 3  # seconds between requests

# Ballet Titles
BALLET_TITLES = [
    "A Legend of Love", "Anna Karenina", "Chopiniana", "Don Quixote", 
    "Grand Pas from the ballet Paquita", "Ivan the Terrible", "La Bayadère",
    "La Fille du Pharaon", "Marco Spada", "Raymonda", "Romeo and Juliet",
    "Spartacus", "Swan Lake", "The Little Humpbacked Horse", "The Nutcracker",
    "The Queen of Spades", "The Sleeping Beauty", "Anyuta", "Carmen Suite",
    "Cipollino", "Coppelia", "Dancemania", "FADING", "Giselle", "JUST",
    "La Sylphide", "Master and Margarita", "SILENTIUM", "The Bright Stream",
    "The Flames of Paris", "The Seagull", "The Tempest"
]

# Local HTML File Path (for offline processing)
LOCAL_HTML_PATH = "../Bolshoi HTML TEST/Bolshoi Theatre • Season.html"
