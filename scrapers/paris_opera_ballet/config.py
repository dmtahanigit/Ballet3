"""
Configuration for the Paris Opera Ballet scraper.

This module contains configuration settings specific to the Paris Opera Ballet scraper,
including URLs, database settings, and scraping parameters.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base URL for the Paris Opera Ballet website
BASE_URL = "https://www.operadeparis.fr/en/season-and-tickets/ballet"

# MongoDB settings
MONGO_URI = os.getenv('MONGODB_URI')
DATABASE_NAME = os.getenv('DATABASE_NAME')
COLLECTION_NAME = os.getenv('COLLECTION_NAME', 'paris_opera_ballet')

# Scraping settings
IMPLICIT_WAIT = 10  # seconds
PAGE_LOAD_TIMEOUT = 30  # seconds
REQUEST_DELAY = 2  # seconds between requests
UPDATE_INTERVAL = 1  # days between scheduled updates

# Selectors for Paris Opera Ballet website
SELECTORS = {
    'show_card': [
        ".show-card",
        "div.show-card",
        "[class*='show-card']",
        "//div[contains(@class, 'show-card')]",
        "//div[contains(@class, 'show')]"
    ],
    'title': [
        "p.show__title",
        ".show__title",
        "h2.title",
        ".title"
    ],
    'link': [
        "a.FeaturedList__reserve-img",
        "a.show__link",
        "a.link"
    ],
    'image': [
        "img",
        ".show__image img",
        ".image img"
    ],
    'venue': [
        "p.show__place span",
        ".show__place span",
        ".venue span"
    ],
    'date': [
        "p.show__date span",
        ".show__date span",
        ".date span"
    ],
    'description': [
        "div.show__description",
        "div.description",
        "div.performance-description",
        "div.show-description",
        "div.content-description",
        "div[itemprop='description']",
        "meta[property='og:description']"
    ],
    'video': [
        "div.video-player",
        "iframe.video-iframe",
        "div.video-container iframe"
    ]
}

# Default descriptions for well-known ballets
DEFAULT_DESCRIPTIONS = {
    "The Nutcracker": "The Nutcracker is a classic holiday ballet that tells the story of Clara, who receives a nutcracker doll as a gift and enters a magical world where the Nutcracker and other characters come to life. This enchanting performance features iconic music by Tchaikovsky and is a beloved tradition of the Paris Opera Ballet.",
    "Swan Lake": "Swan Lake is one of the most iconic classical ballets, telling the story of Odette, a princess turned into a swan by an evil sorcerer's curse. The Paris Opera Ballet's production showcases the company's technical brilliance and artistic expression through Tchaikovsky's magnificent score and the demanding choreography that has captivated audiences for generations.",
    "Giselle": "Giselle is a romantic ballet that tells the story of a peasant girl who dies of a broken heart after discovering her lover is betrothed to another. The Paris Opera Ballet's production highlights the ethereal quality of the second act, where Giselle becomes one of the Wilis, spirits of maidens who died before their wedding day.",
    "Romeo and Juliet": "The Paris Opera Ballet presents Shakespeare's timeless tale of star-crossed lovers through expressive choreography and Prokofiev's powerful score. This production captures the passion, drama, and tragedy of one of the world's greatest love stories.",
    "La Bayadère": "La Bayadère is a dramatic ballet that tells the story of the temple dancer Nikiya and the warrior Solor, who pledge their eternal love to each other. The Paris Opera Ballet's production is known for its spectacular 'Kingdom of the Shades' scene, featuring the corps de ballet in perfect synchronization.",
    "Don Quixote": "Don Quixote is a vibrant, colorful ballet based on episodes from Cervantes' famous novel. The Paris Opera Ballet's production is full of Spanish-inspired dancing, featuring the love story of Kitri and Basilio alongside Don Quixote's quest for his ideal woman."
}

# Cookie consent selectors
COOKIE_SELECTORS = [
    (By.ID, "axeptio_overlay"),
    (By.ID, "axeptio_btn_acceptAll"),
    (By.CSS_SELECTOR, "[data-test='cookie-accept-all']"),
    (By.CSS_SELECTOR, "button[aria-label*='accept']"),
    (By.XPATH, "//button[contains(text(), 'Accept')]")
]
