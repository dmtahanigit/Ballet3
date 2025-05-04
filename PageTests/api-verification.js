/**
 * API Verification Script
 * 
 * This script tests the API server's diagnostic endpoint for description data
 * to verify that descriptions are present in the database without loading the entire page.
 */

// Function to fetch description data from the API
async function fetchDescriptionData() {
  try {
    console.log('Fetching description data from API...');
    const response = await fetch('http://localhost:8000/api/debug/description-test');
    
    if (!response.ok) {
      throw new Error(`API request failed with status: ${response.status}`);
    }
    
    const data = await response.json();
    console.log('API response received:', data);
    
    return data;
  } catch (error) {
    console.error('Error fetching description data:', error);
    return null;
  }
}

// Function to analyze the description data
function analyzeDescriptionData(data) {
  if (!data) {
    return {
      success: false,
      message: 'Failed to fetch description data from API'
    };
  }
  
  // Check if we have performances
  if (data.performance_count === 0) {
    return {
      success: false,
      message: 'No performances found in database'
    };
  }
  
  // Check if all performances have descriptions
  const missingDescriptions = data.performance_count - data.descriptions_present;
  if (missingDescriptions > 0) {
    return {
      success: false,
      message: `${missingDescriptions} performances are missing descriptions`
    };
  }
  
  // Check average description length (should be substantial)
  if (data.average_length < 100) {
    return {
      success: false,
      message: `Average description length (${data.average_length.toFixed(2)}) is suspiciously short`
    };
  }
  
  // Check individual performances
  const shortDescriptions = data.performance_details.filter(p => 
    p.description_length < 100 && p.description_present
  );
  
  if (shortDescriptions.length > 0) {
    return {
      success: true,
      warnings: true,
      message: `All performances have descriptions, but ${shortDescriptions.length} have suspiciously short descriptions`,
      shortDescriptions: shortDescriptions.map(p => p.title)
    };
  }
  
  return {
    success: true,
    warnings: false,
    message: 'All performances have substantial descriptions',
    averageLength: data.average_length.toFixed(2)
  };
}

// Self-executing async function to run the verification
(async () => {
  console.log('=== API DESCRIPTION VERIFICATION ===');
  
  // Fetch data from API
  const data = await fetchDescriptionData();
  
  // Analyze the data
  const analysis = analyzeDescriptionData(data);
  
  // Log the results
  console.log('Verification result:', analysis);
  
  // Make results available globally
  window.apiVerificationResults = {
    rawData: data,
    analysis: analysis
  };
  
  // Return the analysis
  return analysis;
})();
