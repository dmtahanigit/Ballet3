/**
 * Verification Runner Script
 * 
 * This script runs all verification scripts in a memory-efficient way,
 * loading each script one at a time and reporting the results.
 */

// Configuration for verification scripts
const verificationScripts = [
  {
    name: 'Description Verification',
    path: 'description-verification.js',
    resultKey: null, // This script doesn't set a global result variable
    description: 'Verifies that descriptions are properly displayed without truncation or collapsed state'
  },
  {
    name: 'DOM Diffing',
    path: 'dom-diffing.js',
    resultKey: null, // This script captures state but doesn't set a global result variable
    description: 'Captures the current state of performance descriptions for comparison'
  },
  {
    name: 'Incremental Verification',
    path: 'incremental-verification.js',
    resultKey: 'verificationResults',
    description: 'Performs step-by-step verification of the description display fix'
  },
  {
    name: 'API Verification',
    path: 'api-verification.js',
    resultKey: 'apiVerificationResults',
    description: 'Verifies that descriptions are present in the database'
  }
];

// Function to load a script
function loadScript(src) {
  return new Promise((resolve, reject) => {
    const script = document.createElement('script');
    script.src = src;
    script.onload = () => resolve();
    script.onerror = (error) => reject(new Error(`Failed to load script: ${src}`));
    document.head.appendChild(script);
  });
}

// Function to run a verification script
async function runVerification(scriptConfig) {
  console.log(`=== Running ${scriptConfig.name} ===`);
  console.log(scriptConfig.description);
  
  try {
    // Load the script
    await loadScript(scriptConfig.path);
    console.log(`${scriptConfig.name} loaded successfully`);
    
    // Wait a moment for the script to execute
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // Check for results if a result key is specified
    if (scriptConfig.resultKey && window[scriptConfig.resultKey]) {
      console.log(`${scriptConfig.name} results:`, window[scriptConfig.resultKey]);
    } else {
      console.log(`${scriptConfig.name} executed (check console for detailed output)`);
    }
    
    return true;
  } catch (error) {
    console.error(`Error running ${scriptConfig.name}:`, error);
    return false;
  }
}

// Function to run all verification scripts sequentially
async function runAllVerifications() {
  console.log('=== STARTING VERIFICATION PROCESS ===');
  console.log(`Running ${verificationScripts.length} verification scripts...`);
  
  const results = [];
  
  for (const scriptConfig of verificationScripts) {
    const success = await runVerification(scriptConfig);
    results.push({
      name: scriptConfig.name,
      success
    });
    
    // Wait a moment between scripts
    await new Promise(resolve => setTimeout(resolve, 500));
  }
  
  console.log('=== VERIFICATION PROCESS COMPLETE ===');
  console.log('Results summary:');
  results.forEach(result => {
    console.log(`- ${result.name}: ${result.success ? 'Completed' : 'Failed'}`);
  });
  
  return results;
}

// Self-executing function to run all verifications
(async () => {
  // Add a button to the page to run the verification
  const button = document.createElement('button');
  button.textContent = 'Run Verification Scripts';
  button.style.position = 'fixed';
  button.style.top = '10px';
  button.style.right = '10px';
  button.style.zIndex = '9999';
  button.style.padding = '10px';
  button.style.backgroundColor = '#007bff';
  button.style.color = 'white';
  button.style.border = 'none';
  button.style.borderRadius = '5px';
  button.style.cursor = 'pointer';
  
  button.addEventListener('click', async () => {
    button.disabled = true;
    button.textContent = 'Running Verification...';
    
    try {
      await runAllVerifications();
      button.textContent = 'Verification Complete';
      button.style.backgroundColor = '#28a745';
    } catch (error) {
      console.error('Error running verifications:', error);
      button.textContent = 'Verification Failed';
      button.style.backgroundColor = '#dc3545';
    }
    
    // Re-enable after a delay
    setTimeout(() => {
      button.disabled = false;
      button.textContent = 'Run Verification Scripts';
      button.style.backgroundColor = '#007bff';
    }, 5000);
  });
  
  document.body.appendChild(button);
  
  console.log('Verification runner loaded. Click the button in the top-right corner to run all verification scripts.');
})();
