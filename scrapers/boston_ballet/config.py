"""
Configuration for the Boston Ballet scraper.

This module contains configuration settings specific to the Boston Ballet scraper,
including URLs, database settings, and scraping parameters.
"""

import os
from dotenv import load_dotenv
from selenium.webdriver.common.by import By

# Load environment variables
load_dotenv()

# Base URL for the Boston Ballet website
BASE_URL = "https://www.bostonballet.org/Home/Tickets-Performances/"

# MongoDB settings
MONGO_URI = os.getenv('MONGODB_URI')
DATABASE_NAME = os.getenv('DATABASE_NAME')
COLLECTION_NAME = os.getenv('BOSTON_COLLECTION_NAME', 'boston_ballet')

# Scraping settings
IMPLICIT_WAIT = 10  # seconds
PAGE_LOAD_TIMEOUT = 30  # seconds
REQUEST_DELAY = 2  # seconds between requests
UPDATE_INTERVAL = 1  # days between scheduled updates

# Selectors for Boston Ballet website
SELECTORS = {
    'performance': [
        ".performance-item",
        ".event-item",
        ".performance-card",
        ".event-card",
        ".show-item",
        "//div[contains(@class, 'performance')]",
        "//div[contains(@class, 'event')]"
    ],
    'title': [
        ".performance-title",
        ".event-title",
        "h2.title",
        ".title",
        ".card-title"
    ],
    'link': [
        "a.performance-link",
        "a.event-link",
        "a.card-link",
        "a.title-link"
    ],
    'image': [
        "img.performance-image",
        "img.event-image",
        "img.card-image",
        ".image img"
    ],
    'date': [
        ".performance-date",
        ".event-date",
        ".date",
        ".date-range"
    ],
    'description': [
        ".performance-description",
        ".event-description",
        ".description",
        ".card-text",
        "div[itemprop='description']",
        "meta[property='og:description']"
    ],
    'venue': [
        ".performance-venue",
        ".event-venue",
        ".venue",
        ".location"
    ]
}

# Default descriptions for well-known ballets
DEFAULT_DESCRIPTIONS = {
    "The Nutcracker": "The Nutcracker is a classic holiday ballet that tells the story of Clara, who receives a nutcracker doll as a gift and enters a magical world where the Nutcracker and other characters come to life. This enchanting performance features iconic music by Tchaikovsky and is a beloved tradition of the Boston Ballet.",
    "Swan Lake": "Swan Lake is one of the most iconic classical ballets, telling the story of Odette, a princess turned into a swan by an evil sorcerer's curse. The Boston Ballet's production showcases the company's technical brilliance and artistic expression through Tchaikovsky's magnificent score and the demanding choreography that has captivated audiences for generations.",
    "Giselle": "Giselle is a romantic ballet that tells the story of a peasant girl who dies of a broken heart after discovering her lover is betrothed to another. The Boston Ballet's production highlights the ethereal quality of the second act, where Giselle becomes one of the Wilis, spirits of maidens who died before their wedding day.",
    "Romeo and Juliet": "The Boston Ballet presents Shakespeare's timeless tale of star-crossed lovers through expressive choreography and Prokofiev's powerful score. This production captures the passion, drama, and tragedy of one of the world's greatest love stories.",
    "La Bayadère": "La Bayadère is a dramatic ballet that tells the story of the temple dancer Nikiya and the warrior Solor, who pledge their eternal love to each other. The Boston Ballet's production is known for its spectacular 'Kingdom of the Shades' scene, featuring the corps de ballet in perfect synchronization.",
    "Don Quixote": "Don Quixote is a vibrant, colorful ballet based on episodes from Cervantes' famous novel. The Boston Ballet's production is full of Spanish-inspired dancing, featuring the love story of Kitri and Basilio alongside Don Quixote's quest for his ideal woman.",
    "The Sleeping Beauty": "The Sleeping Beauty is a classic ballet based on the fairy tale. The Boston Ballet's production features Tchaikovsky's magnificent score and showcases the company's classical technique and grand style.",
    "Cinderella": "Cinderella is a beloved fairy tale ballet that follows the story of a young woman who, despite her circumstances, finds true love with the help of her fairy godmother. The Boston Ballet's production combines beautiful choreography with Prokofiev's enchanting score.",
    "Coppélia": "Coppélia is a comedic ballet that tells the story of a mysterious doll maker and his lifelike creation. The Boston Ballet's production is known for its charming characters and delightful humor.",
    "A Midsummer Night's Dream": "A Midsummer Night's Dream is a ballet based on Shakespeare's beloved comedy. The Boston Ballet's production brings to life the magical forest, mischievous fairies, and confused lovers with enchanting choreography and Mendelssohn's beautiful music."
}

# Cookie consent selectors
COOKIE_SELECTORS = [
    (By.ID, "cookie-consent"),
    (By.CLASS_NAME, "cookie-consent"),
    (By.CSS_SELECTOR, ".cookie-consent-button"),
    (By.CSS_SELECTOR, "button[data-consent='accept']"),
    (By.XPATH, "//button[contains(text(), 'Accept')]"),
    (By.XPATH, "//button[contains(text(), 'I Agree')]"),
    (By.XPATH, "//button[contains(text(), 'Accept All')]")
]

# Regex patterns for extracting performance data
REGEX_PATTERNS = {
    'date': r'(\w+ \d{1,2}(?:st|nd|rd|th)?,? \d{4}(?:\s*[-–]\s*\w+ \d{1,2}(?:st|nd|rd|th)?,? \d{4})?)',
    'time': r'(\d{1,2}:\d{2}\s*(?:AM|PM|am|pm))',
    'price': r'\$(\d+(?:\.\d{2})?(?:\s*[-–]\s*\$\d+(?:\.\d{2})?)?)'
}
