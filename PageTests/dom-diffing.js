/**
 * DOM Diffing Script for Performance Description Verification
 * 
 * This script captures the state of performance descriptions and allows
 * comparison before and after changes to verify the fix was successful.
 */

// Function to capture the current state of performance descriptions
function captureDescriptionState() {
  // Get all performance items
  const performanceItems = document.querySelectorAll('.performance-item');
  
  // Extract only the relevant information from each item
  return Array.from(performanceItems).map(item => {
    const title = item.querySelector('.performance-title')?.textContent.trim() || 'Unknown';
    const descriptionElement = item.querySelector('.performance-description');
    const readMoreButton = item.querySelector('.read-more-btn');
    
    return {
      title,
      // Description properties
      description: {
        exists: !!descriptionElement,
        hasCollapsedClass: descriptionElement?.classList.contains('collapsed') || false,
        textLength: descriptionElement?.textContent.trim().length || 0,
        isTruncated: descriptionElement?.textContent.trim().endsWith('...') || false,
        text: descriptionElement?.textContent.trim().substring(0, 50) + '...' || ''
      },
      // Read More button properties
      readMoreButton: {
        exists: !!readMoreButton,
        text: readMoreButton?.textContent.trim() || ''
      }
    };
  });
}

// Function to compare before and after states
function compareDescriptionStates(before, after) {
  // Ensure we have the same number of items
  if (before.length !== after.length) {
    return {
      success: false,
      message: `Different number of performance items: Before=${before.length}, After=${after.length}`
    };
  }
  
  // Compare each item
  const differences = [];
  for (let i = 0; i < before.length; i++) {
    const beforeItem = before[i];
    const afterItem = after[i];
    
    // Check for differences
    if (beforeItem.title !== afterItem.title) {
      differences.push(`Item ${i+1}: Title changed from "${beforeItem.title}" to "${afterItem.title}"`);
    }
    
    // Check description changes
    const beforeDesc = beforeItem.description;
    const afterDesc = afterItem.description;
    
    if (beforeDesc.hasCollapsedClass !== afterDesc.hasCollapsedClass) {
      differences.push(`Item ${i+1} (${afterItem.title}): Collapsed class ${afterDesc.hasCollapsedClass ? 'added' : 'removed'}`);
    }
    
    if (beforeDesc.isTruncated !== afterDesc.isTruncated) {
      differences.push(`Item ${i+1} (${afterItem.title}): Truncation ${afterDesc.isTruncated ? 'added' : 'removed'}`);
    }
    
    if (beforeDesc.textLength !== afterDesc.textLength) {
      differences.push(`Item ${i+1} (${afterItem.title}): Text length changed from ${beforeDesc.textLength} to ${afterDesc.textLength}`);
    }
    
    // Check read more button changes
    const beforeBtn = beforeItem.readMoreButton;
    const afterBtn = afterItem.readMoreButton;
    
    if (beforeBtn.exists !== afterBtn.exists) {
      differences.push(`Item ${i+1} (${afterItem.title}): Read More button ${afterBtn.exists ? 'added' : 'removed'}`);
    }
  }
  
  // Determine success based on our criteria
  const success = after.every(item => 
    !item.description.hasCollapsedClass && 
    !item.description.isTruncated && 
    !item.readMoreButton.exists
  );
  
  return {
    success,
    differences,
    message: success 
      ? "All descriptions are properly displayed without collapsed class or truncation, and Read More buttons are removed."
      : "Some issues remain with the description display."
  };
}

// Store the current state (can be used before changes)
window.captureBeforeState = function() {
  window.beforeState = captureDescriptionState();
  console.log('Before state captured:', window.beforeState);
  return window.beforeState;
};

// Compare with current state (can be used after changes)
window.verifyChanges = function() {
  if (!window.beforeState) {
    console.error('No before state captured. Call captureBeforeState() first.');
    return null;
  }
  
  const afterState = captureDescriptionState();
  const comparison = compareDescriptionStates(window.beforeState, afterState);
  
  console.log('Verification result:', comparison);
  if (comparison.differences.length > 0) {
    console.log('Differences detected:');
    comparison.differences.forEach(diff => console.log(' -', diff));
  }
  
  return comparison;
};

// Self-executing function to provide immediate feedback
(() => {
  console.log('DOM Diffing Script loaded. Use window.captureBeforeState() and window.verifyChanges() to test changes.');
  
  // Capture current state automatically
  const currentState = captureDescriptionState();
  console.log('Current description state:', currentState);
  
  // Check if descriptions are already in the desired state
  const allProperlyDisplayed = currentState.every(item => 
    !item.description.hasCollapsedClass && 
    !item.description.isTruncated && 
    !item.readMoreButton.exists
  );
  
  console.log('All descriptions properly displayed:', allProperlyDisplayed);
  
  return {
    currentState,
    allProperlyDisplayed
  };
})();
