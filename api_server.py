from flask import Flask, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import re
from datetime import datetime

load_dotenv()

app = Flask(__name__)
CORS(app)

# MongoDB connection with SSL settings
MONGODB_URI = os.getenv('MONGODB_URI')
DATABASE_NAME = os.getenv('DATABASE_NAME')
COLLECTION_NAME = os.getenv('COLLECTION_NAME')

client = MongoClient(MONGODB_URI)
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]

@app.route('/api/companies/paris-opera-ballet', methods=['GET'])
def get_company_info():
    try:
        return jsonify({
            'name': 'Paris Opera Ballet',
            'description': 'The Paris Opera Ballet is the oldest national ballet company in the world, founded in 1669. It is the ballet company of the Paris Opera and is one of the most prestigious ballet companies in the world.',
            'logo': 'images/pob-logo.png'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def transform_performance(performance):
    """
    Transform performance data from database format to frontend expected format.
    
    This function ensures all required fields are present and correctly formatted,
    particularly handling the date field conversion to startDate and endDate.
    """
    # Create a copy to avoid modifying the original
    transformed = performance.copy()
    
    # Handle date parsing
    if 'date' in performance and performance['date']:
        # Parse date range like "May 7 - June 3, 2024" or "May 2024" or "from 28 Sep to 31 Oct 2025"
        date_str = performance['date']
        
        # Try to match "from X to Y" pattern first (with various formats)
        from_to_match = None
        
        # Pattern 1: from 28 Sep to 31 Oct 2025
        pattern1 = r'from\s+(\d+\s+[A-Za-z]+)\s+to\s+(\d+\s+[A-Za-z]+\s+\d{4})'
        match1 = re.search(pattern1, date_str)
        if match1:
            from_to_match = match1
        
        # Pattern 2: from 01 to 31 Dec 2025
        if not from_to_match:
            pattern2 = r'from\s+(\d+)\s+to\s+(\d+\s+[A-Za-z]+\s+\d{4})'
            match2 = re.search(pattern2, date_str)
            if match2:
                # For this pattern, we need to extract the month from the end date
                # and add it to the start date
                end_date_str = match2.group(2)
                month_match = re.search(r'([A-Za-z]+)', end_date_str)
                if month_match:
                    month = month_match.group(1)
                    start_date_str = f"{match2.group(1)} {month}"
                    # Extract year and add to start date
                    year_match = re.search(r'(\d{4})', end_date_str)
                    if year_match:
                        year = year_match.group(1)
                        start_date_str = f"{start_date_str} {year}"
                        
                    # Now try to parse these dates
                    try:
                        # Try different date formats for start date
                        for fmt in ["%d %B %Y", "%d %b %Y"]:
                            try:
                                start_date = datetime.strptime(start_date_str, fmt)
                                transformed['startDate'] = start_date.strftime("%Y-%m-%d")
                                break
                            except ValueError:
                                continue
                        
                        # Try different date formats for end date
                        for fmt in ["%d %B %Y", "%d %b %Y"]:
                            try:
                                end_date = datetime.strptime(end_date_str, fmt)
                                transformed['endDate'] = end_date.strftime("%Y-%m-%d")
                                break
                            except ValueError:
                                continue
                                
                        # If we successfully parsed the dates, return early
                        if 'startDate' in transformed and 'endDate' in transformed:
                            print(f"Successfully parsed date range for: {performance.get('title', 'Unknown')}")
                            print(f"  Original: {date_str}")
                            print(f"  Parsed: {transformed['startDate']} to {transformed['endDate']}")
                            return transformed
                    except Exception as e:
                        print(f"Error parsing 'from-to' date range '{date_str}': {e}")
                
                # If we get here, we'll continue with other patterns
                from_to_match = match2
        
        # Pattern 3: from 28 Sep to 31 Oct (no year)
        if not from_to_match:
            pattern3 = r'from\s+(\d+\s+[A-Za-z]+)\s+to\s+(\d+\s+[A-Za-z]+)'
            match3 = re.search(pattern3, date_str)
            if match3:
                from_to_match = match3
        
        # Pattern 4: 20 Dec to 31 Dec 2024
        if not from_to_match:
            pattern4 = r'(\d+\s+[A-Za-z]+)\s+to\s+(\d+\s+[A-Za-z]+\s+\d{4})'
            match4 = re.search(pattern4, date_str)
            if match4:
                from_to_match = match4
        
        if from_to_match:
            start_date_str = from_to_match.group(1)
            end_date_str = from_to_match.group(2)
            
            # Extract year from end date
            year_match = re.search(r'\d{4}', end_date_str)
            if year_match:
                year = year_match.group(0)
                # Add year to start date if missing
                if not re.search(r'\d{4}', start_date_str):
                    start_date_str = f"{start_date_str} {year}"
                    
            try:
                # Try different date formats for start date
                for fmt in ["%d %B %Y", "%d %b %Y"]:
                    try:
                        start_date = datetime.strptime(start_date_str, fmt)
                        transformed['startDate'] = start_date.strftime("%Y-%m-%d")
                        break
                    except ValueError:
                        continue
                
                # Try different date formats for end date
                for fmt in ["%d %B %Y", "%d %b %Y"]:
                    try:
                        end_date = datetime.strptime(end_date_str, fmt)
                        transformed['endDate'] = end_date.strftime("%Y-%m-%d")
                        break
                    except ValueError:
                        continue
            except Exception as e:
                print(f"Error parsing 'from-to' date range '{date_str}': {e}")
            
            # If we successfully parsed the dates, return early
            if 'startDate' in transformed and 'endDate' in transformed:
                return transformed
        
        # Try to match "on X at Y" pattern (single date)
        on_pattern = r'on\s+(\d+\s+[A-Za-z]+\s+\d{4})'
        on_match = re.search(on_pattern, date_str)
        
        if on_match:
            single_date_str = on_match.group(1)
            try:
                for fmt in ["%d %B %Y", "%d %b %Y"]:
                    try:
                        date = datetime.strptime(single_date_str, fmt)
                        transformed['startDate'] = date.strftime("%Y-%m-%d")
                        transformed['endDate'] = date.strftime("%Y-%m-%d")
                        break
                    except ValueError:
                        continue
            except Exception as e:
                print(f"Error parsing 'on' date '{single_date_str}': {e}")
                
            # If we successfully parsed the date, return early
            if 'startDate' in transformed and 'endDate' in transformed:
                return transformed
        
        # Try standard date range pattern as fallback
        date_pattern = r'([A-Za-z]+\s+\d+)?\s*-?\s*([A-Za-z]+\s+\d+,?\s+\d{4})'
        match = re.search(date_pattern, date_str)
        
        if match:
            # If we have a range with start and end
            if match.group(1) and match.group(2):
                start_date_str = match.group(1)
                end_date_str = match.group(2)
                
                # Check if year is missing from start date
                if not re.search(r'\d{4}', start_date_str):
                    # Extract year from end date
                    year_match = re.search(r'\d{4}', end_date_str)
                    if year_match:
                        year = year_match.group(0)
                        start_date_str = f"{start_date_str}, {year}"
                
                # Parse dates
                try:
                    # Try different date formats
                    for fmt in ["%B %d, %Y", "%b %d, %Y"]:
                        try:
                            start_date = datetime.strptime(start_date_str, fmt)
                            transformed['startDate'] = start_date.strftime("%Y-%m-%d")
                            break
                        except ValueError:
                            continue
                    
                    for fmt in ["%B %d, %Y", "%b %d, %Y"]:
                        try:
                            end_date = datetime.strptime(end_date_str, fmt)
                            transformed['endDate'] = end_date.strftime("%Y-%m-%d")
                            break
                        except ValueError:
                            continue
                except Exception as e:
                    print(f"Error parsing date range '{date_str}': {e}")
            else:
                # Single date (use as both start and end)
                single_date_str = match.group(2)
                try:
                    for fmt in ["%B %d, %Y", "%b %d, %Y", "%B %Y"]:
                        try:
                            date = datetime.strptime(single_date_str, fmt)
                            transformed['startDate'] = date.strftime("%Y-%m-%d")
                            transformed['endDate'] = date.strftime("%Y-%m-%d")
                            break
                        except ValueError:
                            continue
                except Exception as e:
                    print(f"Error parsing single date '{single_date_str}': {e}")
        
        # Improved fallback: If parsing fails, use the original date string or a more intelligent fallback
        if 'startDate' not in transformed or 'endDate' not in transformed:
            # Log the parsing failure
            print(f"Date parsing failed for: {performance.get('title', 'Unknown')} with date: {date_str}")
            
            # Try to extract year from the date string
            year_match = re.search(r'\d{4}', date_str) if date_str else None
            year = year_match.group(0) if year_match else str(datetime.now().year)
            
            # Try to extract month from the date string
            month_match = re.search(r'(January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)', date_str, re.IGNORECASE) if date_str else None
            
            if month_match:
                month = month_match.group(0)
                # If we have a month, create a date range spanning that month
                month_num = {"january": "01", "february": "02", "march": "03", "april": "04", "may": "05", "june": "06", 
                             "july": "07", "august": "08", "september": "09", "october": "10", "november": "11", "december": "12",
                             "jan": "01", "feb": "02", "mar": "03", "apr": "04", "may": "05", "jun": "06", 
                             "jul": "07", "aug": "08", "sep": "09", "oct": "10", "nov": "11", "dec": "12"}
                             
                month_key = month.lower()
                month_number = month_num.get(month_key, "01")  # Default to January if not found
                
                transformed['startDate'] = f"{year}-{month_number}-01"  # First day of the month
                
                # Last day of the month (simplified)
                last_day = "31" if month_number in ["01", "03", "05", "07", "08", "10", "12"] else "30"
                last_day = "28" if month_number == "02" else last_day  # February (ignoring leap years for simplicity)
                
                transformed['endDate'] = f"{year}-{month_number}-{last_day}"  # Last day of the month
            else:
                # If we can't extract a month, use the original date string as is
                # but format it as a proper date range spanning the year
                transformed['startDate'] = f"{year}-01-01"  # January 1st
                transformed['endDate'] = f"{year}-12-31"  # December 31st
            
            print(f"Using intelligent fallback dates for performance: {performance.get('title', 'Unknown')}")
            print(f"  Original date string: {date_str}")
            print(f"  Fallback date range: {transformed['startDate']} to {transformed['endDate']}")
    
    # Ensure description is properly handled
    if 'description' not in transformed or not transformed['description'] or transformed['description'] == "Description not found":
        # Check if this is one of the performances with a known description
        if performance.get('title') == "The Nutcracker":
            transformed['description'] = "The Nutcracker is a classic holiday ballet that tells the story of Clara, who receives a nutcracker doll as a gift and enters a magical world where the Nutcracker and other characters come to life. This enchanting performance features iconic music by Tchaikovsky and is a beloved tradition of the Paris Opera Ballet."
        elif performance.get('title') == "Swan Lake":
            transformed['description'] = "Swan Lake is one of the most iconic classical ballets, telling the story of Odette, a princess turned into a swan by an evil sorcerer's curse. The Paris Opera Ballet's production showcases the company's technical brilliance and artistic expression through Tchaikovsky's magnificent score and the demanding choreography that has captivated audiences for generations."
        elif performance.get('title') == "Giselle":
            transformed['description'] = "Giselle is a romantic ballet that tells the story of a peasant girl who dies of a broken heart after discovering her lover is betrothed to another. The Paris Opera Ballet's production highlights the ethereal quality of the second act, where Giselle becomes one of the Wilis, spirits of maidens who died before their wedding day."
        elif performance.get('title') == "Romeo and Juliet":
            transformed['description'] = "The Paris Opera Ballet presents Shakespeare's timeless tale of star-crossed lovers through expressive choreography and Prokofiev's powerful score. This production captures the passion, drama, and tragedy of one of the world's greatest love stories."
        else:
            transformed['description'] = "This performance by the Paris Opera Ballet showcases the company's artistic excellence and technical precision. The Paris Opera Ballet is known for its rich heritage and commitment to both classical and contemporary works."
        
        print(f"Added description for: {performance.get('title')}")
    
    # Map thumbnail to image field expected by frontend
    if 'thumbnail' in transformed and transformed['thumbnail']:
        transformed['image'] = transformed['thumbnail']
    
    # Ensure all required fields exist
    required_fields = {
        'id': performance.get('url', performance.get('_id', f"perf_{hash(performance.get('title', 'unknown'))}")),
        'title': performance.get('title', 'Untitled Performance'),
        'image': performance.get('thumbnail', performance.get('image', 'placeholder.jpg')),
        'venue': performance.get('venue', 'Venue information unavailable'),
        'videoUrl': '',
        'isCurrent': False,
        'isNext': False,
        'isPast': False
    }
    
    # Add any missing required fields
    for field, default_value in required_fields.items():
        if field not in transformed or not transformed[field]:
            transformed[field] = default_value
    
    # Calculate if performance is past, current, or upcoming
    try:
        if 'startDate' in transformed and 'endDate' in transformed:
            today = datetime.now().date()
            start_date = datetime.strptime(transformed['startDate'], "%Y-%m-%d").date()
            end_date = datetime.strptime(transformed['endDate'], "%Y-%m-%d").date()
            
            transformed['isPast'] = end_date < today
            transformed['isCurrent'] = start_date <= today <= end_date
    except Exception as e:
        print(f"Error calculating performance timing: {e}")
    
    return transformed

@app.route('/api/companies/paris-opera-ballet/performances', methods=['GET'])
def get_performances():
    try:
        raw_performances = list(collection.find({}, {'_id': 0}))
        transformed_performances = [transform_performance(p) for p in raw_performances]
        return jsonify(transformed_performances)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/debug/performance-transformation', methods=['GET'])
def debug_transformation():
    try:
        # Get a sample performance
        sample = collection.find_one({}, {'_id': 0})
        if not sample:
            return jsonify({"error": "No performances found in database"})
            
        # Show before and after
        transformed = transform_performance(sample)
        
        return jsonify({
            "original": sample,
            "transformed": transformed,
            "fields_added": [k for k in transformed if k not in sample],
            "fields_modified": [k for k in sample if k in transformed and sample[k] != transformed[k]]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/debug/description-test', methods=['GET'])
def debug_description():
    """Lightweight endpoint that returns only description data for testing"""
    try:
        # Get all performances but only retrieve the description field
        performances = list(collection.find({}, {'_id': 0, 'description': 1, 'title': 1}))
        
        if not performances:
            return jsonify({"error": "No performances found in database"})
        
        # Create a lightweight response with just the essential information
        results = []
        for perf in performances:
            description = perf.get('description', '')
            results.append({
                "title": perf.get('title', 'Unknown'),
                "description_present": bool(description),
                "description_length": len(description) if description else 0,
                "description_sample": description[:100] + "..." if description and len(description) > 100 else description
            })
        
        return jsonify({
            "performance_count": len(performances),
            "descriptions_present": sum(1 for p in results if p["description_present"]),
            "average_length": sum(p["description_length"] for p in results) / len(results) if results else 0,
            "performance_details": results
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=5000, help='Port to run the server on')
    args = parser.parse_args()
    app.run(port=args.port, debug=True)
