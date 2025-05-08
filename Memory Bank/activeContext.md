# Active Context

## Current Focus
- Performance data scraping from main listing page
- Individual performance page scraping
- MongoDB integration
- Error handling and recovery
- Frontend thumbnail rendering issue (thumbnails showing as grey boxes despite valid URLs in database)
- Context window optimization when debugging frontend issues

## Recent Changes
- Implemented simplified scraping approach
- Added details_scraped flag for tracking
- Improved error handling
- Added random delays between requests
- Fixed frontend description display issue by:
  - Removing collapsed state and "Read More" buttons
  - Adding explicit styling to ensure descriptions are fully visible
  - Setting max-height to none and overflow to visible
  - Adding fallback text when descriptions are missing
- Removed "Load More" button on Paris Ballet page to show all performances at once
- Updated API port from 5001 to 8000 to match running server
- Implemented advanced testing strategies for frontend changes:
  - Created verification scripts for targeted DOM testing
  - Added diagnostic API endpoint for lightweight verification
  - Implemented DOM diffing for efficient comparison
  - Created memory-optimized verification runner
  - Applied incremental state verification approach
- Fixed frontend thumbnail rendering issue by:
  - Adding a validateImageUrl() function to properly validate image URLs
  - Implementing proper error handling for image loading failures
  - Using a local placeholder image as fallback for invalid or missing images
  - Adding detailed logging for image loading issues
  - Creating a thumbnail-verification.js script to test the fix
- Fixed company logo display issue for Paris Opera Ballet by:
  - Creating a script to scrape the official logo from the Paris Opera Ballet website
  - Downloading the logo directly from the source: https://www.operadeparis.fr/images/universe_opera/logos/universe_logo_pop.png
  - Saving the logo to the correct location in the resources directory
  - Modifying the CSS to preserve the original logo colors by:
    - Removing the white circular background container
    - Removing border-radius, padding, and box-shadow
    - Adding explicit styling to ensure the logo displays at its natural size and colors
    - Setting filter: none to prevent color alterations
  - Updating the HTML to ensure proper sizing of the logo
  - Verifying that the changes display the logo with its original colors

## Next Steps
- Verify the thumbnail rendering fix is working correctly
- Monitor scraping success rate
- Evaluate need for additional selectors
- Consider expanding to other ballet companies
- Add API layer for data access
- Implement additional error handling for edge cases
- Consider adding image optimization for performance

## Technical Considerations
### Context Window Optimization
When resolving frontend issues, we've encountered "context window" errors that limit our ability to process large amounts of code or data at once. To avoid these limitations, we need to implement the following strategies:

#### Surgical Implementation Plan for Description Display Fix
We've developed a precision-focused implementation plan for fixing the description display issue that exemplifies our approach to avoiding context window errors:

1. **Surgical File Targeting**:
   - Target only ui-controller.js and company-page.css
   - Extract only the specific functions and CSS rules that need modification

2. **Precision Editing Technique**:
   - For UI Controller: Modify only the template string that generates description HTML
   - For CSS: Update only the .performance-description rule
   - Remove collapsed state, character limits, and "Read More" buttons

3. **Memory-Optimized Process**:
   - Read one file at a time
   - Extract only the target section
   - Make minimal changes
   - Write back only the modified section
   - Verify before proceeding to next file

#### Modular Approach
- **Targeted File Analysis**: Only load specific files directly related to the issue
- **Incremental Processing**: Analyze one component at a time rather than loading the entire codebase
- **Strategic Sampling**: Examine representative samples of data rather than complete datasets

#### Efficient Debugging
- **Focused Debugging**: Target specific functions rather than entire files
- **Component Isolation**: Extract and test problematic components independently
- **Minimal Reproduction**: Create minimal test cases that reproduce the issue

#### Implementation Techniques
- **Lazy Loading**: Load resources only when needed
- **Chunked Processing**: Process data in manageable chunks
- **Strategic Memoization**: Cache results to avoid recomputation
- **Event Delegation**: Use event delegation for multiple similar elements

#### Advanced Testing Strategies
We've developed elite-level testing strategies to avoid context window errors when verifying frontend changes:

1. **Automated Verification Scripts**:
   - Create lightweight JavaScript snippets that target only specific DOM elements
   - Extract minimal verification data (e.g., presence/absence of classes, element counts)
   - Output results in compact JSON format for easy analysis

2. **Diagnostic API Endpoints**:
   - Add temporary endpoints to the API server for testing specific functionality
   - Return only the minimal data needed for verification
   - Avoid loading entire page content for testing

3. **DOM Diffing Approach**:
   - Capture and compare only relevant DOM structures before and after changes
   - Focus on specific attributes (classes, text content) rather than entire elements
   - Use functional approach to transform DOM into lightweight data structures

4. **Memory-Optimized Browser Testing**:
   - Use headless browser testing with targeted extraction
   - Create scripts that extract only verification data points
   - Process results incrementally to avoid memory pressure

5. **Incremental State Verification**:
   - Implement a state machine approach to testing
   - Verify one aspect at a time (existence, classes, content)
   - Build confidence incrementally without exceeding context limits

These strategies will be particularly important when addressing the thumbnail rendering issue, as it involves multiple components (database, API, frontend rendering) and potentially large datasets.
