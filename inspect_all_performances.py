from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# MongoDB connection settings
MONGODB_URI = os.getenv('MONGODB_URI')
DATABASE_NAME = os.getenv('DATABASE_NAME')
COLLECTION_NAME = os.getenv('COLLECTION_NAME')

# Connect to MongoDB
client = MongoClient(MONGODB_URI)
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]

def inspect_all_performances():
    performances = list(collection.find())
    
    if not performances:
        print("No performances found in the database.")
        return

    print(f"Total number of performances: {len(performances)}")
    
    # Count performances with missing or placeholder descriptions
    missing_descriptions = 0
    placeholder_descriptions = 0
    
    print("\nPerformances that need description updates:")
    print("===========================================")
    
    for i, performance in enumerate(performances, 1):
        title = performance.get('title', 'Untitled')
        url = performance.get('url', 'No URL')
        description = performance.get('description', None)
        
        # Check if description is missing or has placeholder text
        if description is None:
            missing_descriptions += 1
            print(f"{i}. {title} - Missing description - {url}")
        elif description == "Description not found" or description == "Failed to scrape":
            placeholder_descriptions += 1
            print(f"{i}. {title} - Placeholder description - {url}")
    
    print("\nSummary:")
    print(f"Total performances: {len(performances)}")
    print(f"Performances with missing descriptions: {missing_descriptions}")
    print(f"Performances with placeholder descriptions: {placeholder_descriptions}")
    print(f"Performances that need updates: {missing_descriptions + placeholder_descriptions}")
    
    # Print all performances with their descriptions
    print("\nAll Performances:")
    print("================")
    
    for i, performance in enumerate(performances, 1):
        title = performance.get('title', 'Untitled')
        url = performance.get('url', 'No URL')
        description = performance.get('description', 'None')
        
        # Truncate description for display
        short_desc = description[:100] + "..." if description and len(description) > 100 else description
        
        print(f"{i}. {title}")
        print(f"   URL: {url}")
        print(f"   Description: {short_desc}")
        print()

if __name__ == "__main__":
    inspect_all_performances()
