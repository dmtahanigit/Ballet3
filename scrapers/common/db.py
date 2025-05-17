"""
Common database utilities for ballet scrapers.

This module provides shared database functionality for all ballet company scrapers,
ensuring consistent database operations and error handling.
"""

import os
import logging
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# MongoDB connection settings
MONGODB_URI = os.getenv('MONGODB_URI')
DATABASE_NAME = os.getenv('DATABASE_NAME')

def get_mongodb_client():
    """
    Get a MongoDB client instance.
    
    Returns:
        MongoClient: A MongoDB client instance
    
    Raises:
        Exception: If connection to MongoDB fails
    """
    try:
        client = MongoClient(MONGODB_URI)
        # Test the connection
        client.admin.command('ping')
        logger.info("Successfully connected to MongoDB")
        return client
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {str(e)}")
        raise

def get_database():
    """
    Get the MongoDB database instance.
    
    Returns:
        Database: A MongoDB database instance
    """
    client = get_mongodb_client()
    return client[DATABASE_NAME]

def get_collection(collection_name):
    """
    Get a MongoDB collection by name.
    
    Args:
        collection_name (str): Name of the collection
        
    Returns:
        Collection: A MongoDB collection instance
    """
    db = get_database()
    return db[collection_name]

def store_performances(collection, performances):
    """
    Store performances in MongoDB.
    
    Args:
        collection: MongoDB collection
        performances (list): List of performance dictionaries
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        for performance in performances:
            # Use upsert to update existing entries or insert new ones
            # The query is based on the title field, which should be unique
            # within each ballet company's collection
            collection.update_one(
                {'title': performance['title']},
                {'$set': performance},
                upsert=True
            )
        logger.info(f"Stored {len(performances)} performances in MongoDB")
        return True
    except Exception as e:
        logger.error(f"Error storing performances in MongoDB: {str(e)}")
        return False

def get_all_performances(collection_name):
    """
    Get all performances from a collection.
    
    Args:
        collection_name (str): Name of the collection
        
    Returns:
        list: List of performance dictionaries
    """
    try:
        collection = get_collection(collection_name)
        performances = list(collection.find({}, {'_id': 0}))
        logger.info(f"Retrieved {len(performances)} performances from {collection_name}")
        return performances
    except Exception as e:
        logger.error(f"Error retrieving performances from {collection_name}: {str(e)}")
        return []

def search_performances(collection_name, query):
    """
    Search for performances in a collection.
    
    Args:
        collection_name (str): Name of the collection
        query (dict): MongoDB query
        
    Returns:
        list: List of matching performance dictionaries
    """
    try:
        collection = get_collection(collection_name)
        performances = list(collection.find(query, {'_id': 0}))
        logger.info(f"Found {len(performances)} performances matching query in {collection_name}")
        return performances
    except Exception as e:
        logger.error(f"Error searching performances in {collection_name}: {str(e)}")
        return []
