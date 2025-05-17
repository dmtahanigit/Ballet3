"""
Ballet API Server

This module provides a REST API for accessing ballet performance data from
different ballet companies.
"""

import os
import json
import logging
from datetime import datetime
from flask import Flask, jsonify, request, abort
from flask_cors import CORS
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
POB_COLLECTION = os.getenv('COLLECTION_NAME', 'paris_opera_ballet')
BOLSHOI_COLLECTION = os.getenv('BOLSHOI_COLLECTION_NAME', 'bolshoi_ballet')
BOSTON_COLLECTION = os.getenv('BOSTON_COLLECTION_NAME', 'boston_ballet')

# Create Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Connect to MongoDB
try:
    client = MongoClient(MONGODB_URI)
    db = client[DATABASE_NAME]
    logger.info("Connected to MongoDB")
except Exception as e:
    logger.error(f"Failed to connect to MongoDB: {str(e)}")
    raise

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })

@app.route('/api/companies', methods=['GET'])
def get_companies():
    """Get list of available ballet companies."""
    companies = [
        {
            'id': 'paris_opera_ballet',
            'name': 'Paris Opera Ballet',
            'country': 'France',
            'website': 'https://www.operadeparis.fr/en/season-and-tickets/ballet'
        },
        {
            'id': 'bolshoi_ballet',
            'name': 'Bolshoi Ballet',
            'country': 'Russia',
            'website': 'https://www.bolshoi.ru/en/season/'
        },
        {
            'id': 'boston_ballet',
            'name': 'Boston Ballet',
            'country': 'United States',
            'website': 'https://www.bostonballet.org/Home/Tickets-Performances/'
        }
    ]
    return jsonify(companies)

@app.route('/api/performances', methods=['GET'])
def get_all_performances():
    """Get performances from all companies."""
    try:
        # Get query parameters
        limit = request.args.get('limit', default=100, type=int)
        skip = request.args.get('skip', default=0, type=int)
        
        # Get performances from Paris Opera Ballet
        pob_performances = list(db[POB_COLLECTION].find({}, {'_id': 0}))
        
        # Get performances from Bolshoi Ballet
        bolshoi_performances = list(db[BOLSHOI_COLLECTION].find({}, {'_id': 0}))
        
        # Get performances from Boston Ballet
        boston_performances = list(db[BOSTON_COLLECTION].find({}, {'_id': 0}))
        
        # Combine performances
        all_performances = pob_performances + bolshoi_performances + boston_performances
        
        # Apply pagination
        paginated_performances = all_performances[skip:skip+limit]
        
        return jsonify({
            'total': len(all_performances),
            'limit': limit,
            'skip': skip,
            'data': paginated_performances
        })
    except Exception as e:
        logger.error(f"Error getting all performances: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/performances/<company_id>', methods=['GET'])
def get_company_performances(company_id):
    """Get performances for a specific company."""
    try:
        # Validate company ID
        if company_id not in ['paris_opera_ballet', 'bolshoi_ballet', 'boston_ballet']:
            return jsonify({'error': 'Invalid company ID'}), 400
        
        # Get query parameters
        limit = request.args.get('limit', default=100, type=int)
        skip = request.args.get('skip', default=0, type=int)
        
        # Get collection name based on company ID
        if company_id == 'paris_opera_ballet':
            collection_name = POB_COLLECTION
        elif company_id == 'bolshoi_ballet':
            collection_name = BOLSHOI_COLLECTION
        else:  # boston_ballet
            collection_name = BOSTON_COLLECTION
        
        # Get performances
        performances = list(db[collection_name].find({}, {'_id': 0}).skip(skip).limit(limit))
        total_count = db[collection_name].count_documents({})
        
        return jsonify({
            'total': total_count,
            'limit': limit,
            'skip': skip,
            'data': performances
        })
    except Exception as e:
        logger.error(f"Error getting performances for {company_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/performances/<company_id>/<performance_id>', methods=['GET'])
def get_performance(company_id, performance_id):
    """Get a specific performance by ID."""
    try:
        # Validate company ID
        if company_id not in ['paris_opera_ballet', 'bolshoi_ballet', 'boston_ballet']:
            return jsonify({'error': 'Invalid company ID'}), 400
        
        # Get collection name based on company ID
        if company_id == 'paris_opera_ballet':
            collection_name = POB_COLLECTION
        elif company_id == 'bolshoi_ballet':
            collection_name = BOLSHOI_COLLECTION
        else:  # boston_ballet
            collection_name = BOSTON_COLLECTION
        
        # Get performance
        performance = db[collection_name].find_one({'_id': performance_id}, {'_id': 0})
        
        if not performance:
            return jsonify({'error': 'Performance not found'}), 404
        
        return jsonify(performance)
    except Exception as e:
        logger.error(f"Error getting performance {performance_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/search', methods=['GET'])
def search_performances():
    """Search performances across all companies."""
    try:
        # Get query parameters
        query = request.args.get('q', default='', type=str)
        company = request.args.get('company', default='', type=str)
        limit = request.args.get('limit', default=100, type=int)
        skip = request.args.get('skip', default=0, type=int)
        
        if not query:
            return jsonify({'error': 'Query parameter "q" is required'}), 400
        
        # Build MongoDB query
        mongo_query = {
            '$or': [
                {'title': {'$regex': query, '$options': 'i'}},
                {'description': {'$regex': query, '$options': 'i'}}
            ]
        }
        
        # Add company filter if specified
        if company:
            if company not in ['paris_opera_ballet', 'bolshoi_ballet', 'boston_ballet']:
                return jsonify({'error': 'Invalid company ID'}), 400
            mongo_query['company'] = company
        
        # Get collections to search
        collections = []
        if not company or company == 'paris_opera_ballet':
            collections.append(POB_COLLECTION)
        if not company or company == 'bolshoi_ballet':
            collections.append(BOLSHOI_COLLECTION)
        if not company or company == 'boston_ballet':
            collections.append(BOSTON_COLLECTION)
        
        # Search performances
        results = []
        for collection_name in collections:
            collection_results = list(db[collection_name].find(mongo_query, {'_id': 0}))
            results.extend(collection_results)
        
        # Apply pagination
        paginated_results = results[skip:skip+limit]
        
        return jsonify({
            'total': len(results),
            'limit': limit,
            'skip': skip,
            'data': paginated_results
        })
    except Exception as e:
        logger.error(f"Error searching performances: {str(e)}")
        return jsonify({'error': str(e)}), 500

def main():
    """Run the Flask app."""
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting Ballet API server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)

if __name__ == '__main__':
    main()
