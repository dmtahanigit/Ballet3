# Description Display Verification Scripts

This directory contains a set of verification scripts designed to test the description display fix in a memory-efficient way. These scripts implement advanced testing strategies to avoid context window errors when verifying frontend changes.

## Overview

The verification scripts are designed to be run in a browser environment and provide detailed feedback on the state of performance descriptions on the Paris Opera Ballet page. They use a variety of techniques to minimize memory usage and avoid context window errors.

## Scripts

### 1. `verification.html`

A simple HTML page that provides a user interface for running the verification scripts. It includes instructions on how to use the scripts and a button to load the verification runner.

### 2. `run-verification.js`

The main verification runner script that loads and runs all other verification scripts in a memory-efficient way. It adds a button to the Paris Opera Ballet page that, when clicked, runs all verification scripts sequentially and reports the results.

### 3. `description-verification.js`

A basic verification script that checks if descriptions are properly displayed without truncation or collapsed state. It performs the following checks:
- Verifies that descriptions exist
- Checks for the absence of the `.collapsed` class
- Confirms that "Read More" buttons are not present
- Verifies that descriptions are not truncated

### 4. `dom-diffing.js`

A script that captures the current state of performance descriptions and allows comparison before and after changes. It provides functions to:
- Capture the current state of descriptions
- Compare before and after states
- Identify specific differences in the DOM structure

### 5. `incremental-verification.js`

A script that implements a state machine approach to testing, verifying one aspect of the fix at a time. It breaks down the verification process into smaller steps to avoid context window errors:
1. Check if descriptions exist
2. Check for collapsed class
3. Check for "Read More" buttons
4. Check for text truncation
5. Check text lengths

### 6. `api-verification.js`

A script that tests the API server's diagnostic endpoint for description data. It verifies that descriptions are present in the database without loading the entire page content.

## How to Use

1. Make sure the API server is running on `http://localhost:8000`
2. Open `verification.html` in a browser
3. Click the "Open Paris Opera Ballet HTML" button to open the Paris Opera Ballet page in a new tab
4. Click the "Load Verification Runner" button in the verification page
5. Go to the Paris Opera Ballet tab and click the "Run Verification Scripts" button that appears in the top-right corner
6. Check the browser console for detailed verification results

## API Endpoint

The verification scripts use a diagnostic API endpoint added to the API server:

```
GET http://localhost:8000/api/debug/description-test
```

This endpoint returns lightweight information about performance descriptions in the database, including:
- Number of performances
- Number of descriptions present
- Average description length
- Sample of each description

## Memory Optimization Techniques

These scripts implement several memory optimization techniques:

1. **Surgical Targeting**: Each script focuses on specific DOM elements rather than the entire page
2. **Incremental Processing**: Verification is broken down into smaller steps
3. **Minimal Data Extraction**: Only essential data is extracted and processed
4. **Sequential Execution**: Scripts are loaded and run one at a time
5. **Functional Approach**: DOM elements are transformed into lightweight data structures

## Extending the Verification Scripts

To add new verification scripts:

1. Create a new JavaScript file in the PageTests directory
2. Implement the verification logic
3. Add the script to the `verificationScripts` array in `run-verification.js`

## Troubleshooting

If you encounter issues with the verification scripts:

1. Check that the API server is running
2. Verify that the Paris Opera Ballet HTML file is loading correctly
3. Check the browser console for error messages
4. Try running individual verification scripts directly in the browser console
