# Technical Context

## Technologies Used

### Backend

- **Python 3.8+**: Core programming language
- **Flask**: Web framework for the API server
- **Flask-CORS**: CORS support for the API
- **MongoDB**: NoSQL database for storing performance data
- **PyMongo**: MongoDB driver for Python
- **BeautifulSoup4**: HTML parsing for web scraping
- **Requests**: HTTP library for making web requests
- **Selenium**: Browser automation for JavaScript-heavy pages
- **Schedule**: Job scheduling for periodic scraping
- **python-dotenv**: Environment variable management

### Frontend

#### Legacy Frontend (PageTests)
- **HTML/CSS/JavaScript**: Core web technologies
- **Fetch API**: For making requests to the API server

#### New Frontend Architecture (WorldBallet-Apr27Release)
- **HTML5/CSS3/ES6+**: Modern web technologies
- **CSS Grid/Flexbox**: For responsive layouts
- **Fetch API**: For making requests to the API server
- **localStorage**: For client-side caching
- **Module Pattern**: For code organization and encapsulation
- **Async/Await**: For asynchronous operations
- **JSON**: For data interchange

### Testing

- **pytest**: Testing framework
- **pytest-mock**: Mocking library for pytest
- **unittest.mock**: Standard library mocking

### Development Tools

- **black**: Code formatting
- **flake8**: Linting
- **isort**: Import sorting

## Development Setup

### Environment Variables

The application uses the following environment variables, which should be defined in a `.env` file:

```
MONGODB_URI=mongodb://localhost:27017/
DATABASE_NAME=ballet_world
COLLECTION_NAME=paris_opera_ballet
BOLSHOI_COLLECTION_NAME=bolshoi_ballet
BOSTON_COLLECTION_NAME=boston_ballet
PORT=5000
DEBUG=True
```

### MongoDB Setup

The application requires a MongoDB instance. The database structure is as follows:

- **Database**: `ballet_world` (configurable)
- **Collections**:
  - `paris_opera_ballet`: Performances from Paris Opera Ballet
  - `bolshoi_ballet`: Performances from Bolshoi Ballet
  - `boston_ballet`: Performances from Boston Ballet

### Running the Application

The application can be run using the `run.py` script:

```bash
# Run the Paris Opera Ballet scraper
python run.py pob

# Run the Bolshoi Ballet scraper
python run.py bolshoi

# Run the Boston Ballet scraper
python run.py boston

# Run the API server
python run.py api

# Run everything
python run.py all
```

### Testing

Tests can be run using pytest:

```bash
# Run all tests
pytest

# Run specific tests
pytest scrapers/paris_opera_ballet/tests/
pytest scrapers/bolshoi_ballet/tests/
pytest scrapers/boston_ballet/tests/
```

### Frontend Development

The new frontend architecture is located in the `PageTests/WorldBallet-Apr27Release/` directory. It follows a modular structure:

```
WorldBallet-Apr27Release/
├── css/
│   ├── styles.css             # Global styles
│   └── company-page.css       # Company page specific styles
├── images/
│   ├── logo.svg               # Site logo
│   └── placeholder-logo.svg   # Placeholder for company logos
├── js/
│   ├── ballet-data-service.js # Data service for API communication
│   ├── mock-data.js           # Mock data for fallback
│   └── ui-controllers/
│       ├── company-page.js    # Company page controller
│       └── ...                # Other page controllers
└── *.html                     # HTML templates
```

To run the frontend:

1. Start the API server:
   ```
   python run.py api
   ```

2. Open the HTML files in a browser:
   ```
   open PageTests/WorldBallet-Apr27Release/company.html?id=paris_opera_ballet
   open PageTests/WorldBallet-Apr27Release/company.html?id=bolshoi_ballet
   open PageTests/WorldBallet-Apr27Release/company.html?id=boston_ballet
   ```

## Technical Constraints

### Web Scraping

- **Rate Limiting**: Scrapers implement delays between requests to avoid overloading the target websites
- **HTML Structure Changes**: Scrapers need to be robust against changes in the target websites' HTML structure
- **JavaScript-Heavy Pages**: Some pages require Selenium for proper scraping due to dynamic content

### Database

- **Document Size**: MongoDB has a 16MB document size limit
- **Performance**: Large collections may require indexing for optimal performance

### API

- **Rate Limiting**: No rate limiting is currently implemented
- **Authentication**: No authentication is currently implemented

### Frontend

- **Browser Compatibility**: The frontend is designed to work with modern browsers (Chrome, Firefox, Safari, Edge)
- **Responsive Design**: The frontend uses CSS Grid and Flexbox for responsive layouts
- **Offline Support**: The frontend provides mock data fallback when the API is unavailable
- **LocalStorage Limits**: Browser localStorage has size limits (typically 5-10MB)

## Dependencies

The project has the following dependencies, as defined in `requirements.txt`:

```
# Core dependencies
pymongo==4.5.0
python-dotenv==1.0.0
requests==2.31.0
beautifulsoup4==4.12.2
selenium==4.15.2
schedule==1.2.0
Flask==2.3.3
Flask-CORS==4.0.0

# Testing dependencies
pytest==7.4.3
pytest-mock==3.12.0

# Development dependencies
black==23.10.1
flake8==6.1.0
isort==5.12.0
```

## Performance Considerations

- **Scraping Performance**: Web scraping can be slow, especially with Selenium
- **Database Queries**: Large collections may require indexing for optimal performance
- **API Response Time**: Large responses may need pagination or filtering
- **Frontend Caching**: Client-side caching improves performance by reducing API calls
- **Image Optimization**: Images should be optimized for web to reduce load times
- **Code Splitting**: JavaScript code is organized into modules for better maintainability and performance

## Security Considerations

- **Input Validation**: API inputs should be validated to prevent injection attacks
- **CORS**: CORS is enabled for all origins, which may need to be restricted in production
- **Environment Variables**: Sensitive information should be stored in environment variables
- **Error Handling**: Error messages should not expose sensitive information
- **Content Security Policy**: CSP headers should be implemented to prevent XSS attacks
- **HTTPS**: Production deployment should use HTTPS to encrypt data in transit

## Frontend Architecture

The new frontend architecture follows a clean separation of concerns with three distinct layers:

### Data Layer

The data layer is responsible for fetching, processing, and caching data:

- **ballet-data-service.js**: Provides a unified interface for accessing data from the API
- **Cache Manager**: Handles client-side caching with localStorage
- **Mock Data**: Provides fallback data when the API is unavailable

Key features:
- Asynchronous data fetching with async/await
- Error handling with try/catch
- Client-side caching with localStorage
- Cache versioning for handling data structure changes
- Cache expiry for ensuring data freshness
- Mock data fallback for offline development and testing

### UI Layer

The UI layer is responsible for business logic and DOM manipulation:

- **UI Controllers**: Separate modules for each page type
- **Event Handlers**: Manage user interactions
- **DOM Manipulation**: Update the UI based on data changes

Key features:
- Module pattern for encapsulation
- Event-driven architecture
- Separation of business logic from DOM manipulation
- Responsive design with CSS Grid and Flexbox

### View Layer

The view layer defines the structure and appearance of the UI:

- **HTML Templates**: Define the structure of each page
- **CSS Styles**: Define the appearance of UI elements

Key features:
- Semantic HTML5 markup
- CSS3 with Grid and Flexbox for responsive layouts
- Mobile-first design approach
- Progressive enhancement
