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

def inspect_performances():
    performances = list(collection.find())
    
    if not performances:
        print("No performances found in the database.")
        return

    print(f"Total number of performances: {len(performances)}")
    print("\nField names:")
    print(", ".join(performances[0].keys()))

    print("\nSample performance data:")
    for i, performance in enumerate(performances[:3], 1):
        print(f"\nPerformance {i}:")
        for key, value in performance.items():
            if key == 'thumbnail':
                print(f"{key}: {value[:100]}..." if value else f"{key}: None")
            elif key == 'description':
                print(f"{key}: {value}" if value else f"{key}: None")
            else:
                print(f"{key}: {value}")

    # Check for missing thumbnails or descriptions
    missing_thumbnails = sum(1 for p in performances if not p.get('thumbnail'))
    missing_descriptions = sum(1 for p in performances if not p.get('description'))

    print(f"\nPerformances missing thumbnails: {missing_thumbnails}")
    print(f"Performances missing descriptions: {missing_descriptions}")

if __name__ == "__main__":
    inspect_performances()
