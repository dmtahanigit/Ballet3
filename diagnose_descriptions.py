import requests
import json
from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# MongoDB connection settings
MONGODB_URI = os.getenv('MONGODB_URI')
DATABASE_NAME = os.getenv('DATABASE_NAME')
COLLECTION_NAME = os.getenv('COLLECTION_NAME')

def diagnose_descriptions():
    """
    Diagnose the state of ballet descriptions across the system:
    1. Check raw database content
    2. Check API response
    3. Check what the frontend is receiving
    """
    print("\n=== BALLET DESCRIPTION DIAGNOSTIC ===\n")
    
    # Connect to MongoDB
    try:
        print("Connecting to MongoDB...")
        client = MongoClient(MONGODB_URI)
        db = client[DATABASE_NAME]
        collection = db[COLLECTION_NAME]
        
        # Check raw database content
        print("\n--- DATABASE CHECK ---")
        db_performances = list(collection.find({}, {"title": 1, "description": 1, "_id": 0}))
        
        if not db_performances:
            print("No performances found in database!")
            return
            
        print(f"Found {len(db_performances)} performances in database")
        
        # Count performances with missing descriptions
        missing_desc_count = sum(1 for p in db_performances 
                               if 'description' not in p or not p['description'] or p['description'] == "Description not found")
        
        print(f"Performances with missing descriptions: {missing_desc_count}/{len(db_performances)}")
        
        # Show sample of performances with their description status
        print("\nSample performances from database:")
        for i, perf in enumerate(db_performances[:5], 1):
            title = perf.get('title', 'Unknown')
            desc = perf.get('description', 'None')
            desc_status = "MISSING" if not desc or desc == "Description not found" else f"PRESENT ({len(desc)} chars)"
            print(f"  {i}. {title}: Description {desc_status}")
            
        # Check API response
        print("\n--- API CHECK ---")
        try:
            print("Checking API debug endpoint...")
            api_response = requests.get("http://localhost:8000/api/debug/description-test", timeout=5)
            
            if api_response.status_code == 200:
                api_data = api_response.json()
                print(f"API reports {api_data.get('performance_count', 0)} performances")
                print(f"Descriptions present: {api_data.get('descriptions_present', 0)}/{api_data.get('performance_count', 0)}")
                print(f"Average description length: {api_data.get('average_length', 0):.1f} characters")
                
                print("\nSample performances from API:")
                for i, perf in enumerate(api_data.get('performance_details', [])[:5], 1):
                    title = perf.get('title', 'Unknown')
                    desc_present = perf.get('description_present', False)
                    desc_length = perf.get('description_length', 0)
                    desc_status = "MISSING" if not desc_present else f"PRESENT ({desc_length} chars)"
                    print(f"  {i}. {title}: Description {desc_status}")
            else:
                print(f"API returned error: {api_response.status_code}")
                
        except Exception as e:
            print(f"Error checking API: {str(e)}")
            
        # Check what the frontend is receiving
        print("\n--- FRONTEND DATA CHECK ---")
        try:
            print("Checking what data the frontend is receiving...")
            frontend_data_response = requests.get("http://localhost:8000/api/companies/paris-opera-ballet/performances", timeout=5)
            
            if frontend_data_response.status_code == 200:
                frontend_data = frontend_data_response.json()
                print(f"Frontend receives data for {len(frontend_data)} performances")
                
                # Count performances with missing descriptions in frontend data
                missing_frontend_desc = sum(1 for p in frontend_data 
                                         if 'description' not in p or not p['description'] or p['description'] == "Description not found")
                
                print(f"Performances with missing descriptions in frontend data: {missing_frontend_desc}/{len(frontend_data)}")
                
                # Check if API is adding fallback descriptions
                fallback_desc_count = sum(1 for p in frontend_data 
                                       if p.get('description') and p.get('description') != "Description not found" 
                                       and any(p in p.get('description') for p in ["showcases the company's", "artistic excellence"]))
                
                if fallback_desc_count > 0:
                    print(f"API appears to be adding {fallback_desc_count} fallback descriptions")
                
                print("\nSample performances from frontend data:")
                for i, perf in enumerate(frontend_data[:5], 1):
                    title = perf.get('title', 'Unknown')
                    desc = perf.get('description', 'None')
                    desc_status = "MISSING" if not desc or desc == "Description not found" else f"PRESENT ({len(desc)} chars)"
                    print(f"  {i}. {title}: Description {desc_status}")
                    if desc and desc != "Description not found" and len(desc) > 0:
                        print(f"     Sample: {desc[:100]}...")
            else:
                print(f"Frontend data endpoint returned error: {frontend_data_response.status_code}")
                
        except Exception as e:
            print(f"Error checking frontend data: {str(e)}")
            
        # Diagnosis summary
        print("\n=== DIAGNOSIS SUMMARY ===")
        if missing_desc_count > 0 and missing_desc_count == len(db_performances):
            print("DIAGNOSIS: All descriptions are missing in the database.")
            print("RECOMMENDATION: Run the update_ballet_descriptions.py script to scrape and update descriptions.")
        elif missing_desc_count > 0:
            print(f"DIAGNOSIS: {missing_desc_count}/{len(db_performances)} descriptions are missing in the database.")
            print("RECOMMENDATION: Run the update_ballet_descriptions.py script to update missing descriptions.")
        elif missing_frontend_desc > 0 and missing_desc_count == 0:
            print("DIAGNOSIS: Descriptions exist in database but are not being properly served to the frontend.")
            print("RECOMMENDATION: Check the API transformation logic in api_server.py.")
        else:
            print("DIAGNOSIS: No clear issues found with descriptions.")
            print("RECOMMENDATION: Check the frontend code for display issues.")
            
    except Exception as e:
        print(f"Error during diagnosis: {str(e)}")

if __name__ == "__main__":
    diagnose_descriptions()
