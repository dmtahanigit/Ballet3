"""
Configuration for the Bolshoi Ballet scraper.

This module contains configuration settings specific to the Bolshoi Ballet scraper,
including URLs, database settings, and scraping parameters.
"""

import os
from dotenv import load_dotenv
from selenium.webdriver.common.by import By

# Load environment variables
load_dotenv()

# Base URL for the Bolshoi Theatre website
BASE_URL = "https://www.bolshoi.ru/en/season/"
LOCAL_HTML_PATH = "../Bolshoi HTML TEST/Bolshoi Theatre • Season.html"

# MongoDB settings
MONGO_URI = os.getenv('MONGODB_URI')
DATABASE_NAME = os.getenv('DATABASE_NAME')
COLLECTION_NAME = os.getenv('BOLSHOI_COLLECTION_NAME', 'bolshoi_ballet')

# Scraping settings
IMPLICIT_WAIT = 10  # seconds
PAGE_LOAD_TIMEOUT = 30  # seconds
REQUEST_DELAY = 3  # seconds between requests
UPDATE_INTERVAL = 1  # days between scheduled updates

# List of known ballet titles to look for
BALLET_TITLES = [
    "Swan Lake",
    "The Nutcracker",
    "Giselle",
    "Don Quixote",
    "La Bayadère",
    "Romeo and Juliet",
    "Spartacus",
    "The Sleeping Beauty",
    "Jewels",
    "Le Corsaire",
    "The Bright Stream",
    "The Flames of Paris",
    "The Golden Age",
    "The Taming of the Shrew",
    "A Hero of Our Time",
    "Raymonda",
    "La Sylphide",
    "The Pharaoh's Daughter",
    "The Legend of Love",
    "Ivan the Terrible"
]

# Selectors for Bolshoi Theatre website
SELECTORS = {
    'performance': [
        ".performance-item",
        ".event-item",
        ".show-item",
        "//div[contains(@class, 'performance')]",
        "//div[contains(@class, 'event')]"
    ],
    'title': [
        ".performance-title",
        ".event-title",
        "h2.title",
        ".title"
    ],
    'date': [
        ".performance-date",
        ".event-date",
        ".date"
    ],
    'description': [
        ".performance-description",
        ".event-description",
        ".description",
        "div[itemprop='description']",
        "meta[property='og:description']"
    ],
    'composer': [
        ".performance-composer",
        ".event-composer",
        ".composer"
    ],
    'venue': [
        ".performance-venue",
        ".event-venue",
        ".venue"
    ]
}

# Default descriptions for well-known ballets
DEFAULT_DESCRIPTIONS = {
    "Swan Lake": "Swan Lake is one of the most iconic classical ballets, featuring Tchaikovsky's magnificent score. The Bolshoi Theatre's production showcases the company's technical brilliance and artistic expression through the demanding choreography that has captivated audiences for generations.",
    "The Nutcracker": "The Nutcracker is a classic holiday ballet that tells the story of Clara, who receives a nutcracker doll as a gift and enters a magical world where the Nutcracker and other characters come to life. This enchanting performance features iconic music by Tchaikovsky and is a beloved tradition of the Bolshoi Theatre.",
    "Giselle": "Giselle is a romantic ballet that tells the story of a peasant girl who dies of a broken heart after discovering her lover is betrothed to another. The Bolshoi Theatre's production highlights the ethereal quality of the second act, where Giselle becomes one of the Wilis, spirits of maidens who died before their wedding day.",
    "Romeo and Juliet": "The Bolshoi Theatre presents Shakespeare's timeless tale of star-crossed lovers through expressive choreography and Prokofiev's powerful score. This production captures the passion, drama, and tragedy of one of the world's greatest love stories.",
    "La Bayadère": "La Bayadère is a dramatic ballet that tells the story of the temple dancer Nikiya and the warrior Solor, who pledge their eternal love to each other. The Bolshoi Theatre's production is known for its spectacular 'Kingdom of the Shades' scene, featuring the corps de ballet in perfect synchronization.",
    "Don Quixote": "Don Quixote is a vibrant, colorful ballet based on episodes from Cervantes' famous novel. The Bolshoi Theatre's production is full of Spanish-inspired dancing, featuring the love story of Kitri and Basilio alongside Don Quixote's quest for his ideal woman.",
    "Spartacus": "Spartacus is a ballet that tells the story of the gladiator who led a slave uprising against the Roman Republic. The Bolshoi Theatre's production is known for its powerful and athletic male dancing, particularly in the role of Spartacus.",
    "The Sleeping Beauty": "The Sleeping Beauty is a classic ballet based on the fairy tale. The Bolshoi Theatre's production features Tchaikovsky's magnificent score and showcases the company's classical technique and grand style.",
    "Jewels": "Jewels is a three-act plotless ballet created by George Balanchine. Each act represents a different gemstone: Emeralds, Rubies, and Diamonds. The Bolshoi Theatre's production highlights the company's versatility in different ballet styles.",
    "Le Corsaire": "Le Corsaire is a ballet about the love between a pirate and a beautiful slave girl. The Bolshoi Theatre's production is known for its spectacular pas de deux and virtuosic dancing."
}

# Cookie consent selectors
COOKIE_SELECTORS = [
    (By.ID, "cookie-consent"),
    (By.CLASS_NAME, "cookie-consent"),
    (By.CSS_SELECTOR, ".cookie-consent-button"),
    (By.CSS_SELECTOR, "button[data-consent='accept']"),
    (By.XPATH, "//button[contains(text(), 'Accept')]"),
    (By.XPATH, "//button[contains(text(), 'I Agree')]")
]

# Regex patterns for extracting performance data
REGEX_PATTERNS = {
    'ballet_section': r'Ballet\s+(?:in|by).*?(?:\d+\+|$)',
    'title': r'Ballet\s+(?:in|by).*?\n\s*(.*?)(?:\n|$)',
    'composer': r'((?:to music by|by).*?)(?:\n|\d+\+|$)',
    'date': r'(\d+\s+\w+\s+\d{4}\s+[-–]\s+\d+\s+\w+\s+\d{4}|\d+\s+[-–]\s+\d+\s+\w+\s+\d{4})',
    'age_restriction': r'(\d+\+)',
    'ballet_type': r'(Ballet\s+(?:in|by).*?)(?:\n|$)'
}
