/**
 * Incremental State Verification Script
 * 
 * This script implements a state machine approach to testing the description display fix,
 * verifying one aspect at a time to avoid context window errors.
 */

// State machine for verification
const VerificationStateMachine = {
  // Current state
  currentState: 'initial',
  
  // Results storage
  results: {},
  
  // State definitions and transitions
  states: {
    'initial': {
      execute: function() {
        console.log('=== INCREMENTAL VERIFICATION STARTED ===');
        console.log('Step 1: Checking if descriptions exist...');
        
        const descriptions = document.querySelectorAll('.performance-description');
        const descriptionsExist = descriptions.length > 0;
        
        this.results.descriptionsExist = descriptionsExist;
        this.results.descriptionCount = descriptions.length;
        
        console.log(`Found ${descriptions.length} description elements.`);
        
        return descriptionsExist ? 'checkCollapsedClass' : 'failure';
      }
    },
    
    'checkCollapsedClass': {
      execute: function() {
        console.log('Step 2: Checking for collapsed class...');
        
        const descriptions = document.querySelectorAll('.performance-description');
        const collapsedDescriptions = Array.from(descriptions).filter(d => 
          d.classList.contains('collapsed')
        );
        
        this.results.hasCollapsedClass = collapsedDescriptions.length > 0;
        this.results.collapsedCount = collapsedDescriptions.length;
        
        console.log(`Found ${collapsedDescriptions.length} descriptions with collapsed class.`);
        
        return this.results.hasCollapsedClass ? 'failure' : 'checkReadMoreButtons';
      }
    },
    
    'checkReadMoreButtons': {
      execute: function() {
        console.log('Step 3: Checking for Read More buttons...');
        
        const readMoreButtons = document.querySelectorAll('.read-more-btn');
        
        this.results.hasReadMoreButtons = readMoreButtons.length > 0;
        this.results.readMoreButtonCount = readMoreButtons.length;
        
        console.log(`Found ${readMoreButtons.length} Read More buttons.`);
        
        return this.results.hasReadMoreButtons ? 'failure' : 'checkTruncation';
      }
    },
    
    'checkTruncation': {
      execute: function() {
        console.log('Step 4: Checking for text truncation...');
        
        const descriptions = document.querySelectorAll('.performance-description');
        const truncatedDescriptions = Array.from(descriptions).filter(d => 
          d.textContent.trim().endsWith('...')
        );
        
        this.results.hasTruncatedText = truncatedDescriptions.length > 0;
        this.results.truncatedCount = truncatedDescriptions.length;
        
        console.log(`Found ${truncatedDescriptions.length} descriptions with truncated text.`);
        
        return this.results.hasTruncatedText ? 'failure' : 'checkTextLength';
      }
    },
    
    'checkTextLength': {
      execute: function() {
        console.log('Step 5: Checking text lengths...');
        
        const descriptions = document.querySelectorAll('.performance-description');
        const textLengths = Array.from(descriptions).map(d => d.textContent.trim().length);
        
        // Check if any descriptions are suspiciously short (less than 100 chars)
        const shortDescriptions = textLengths.filter(length => length < 100);
        
        this.results.textLengths = textLengths;
        this.results.hasShortDescriptions = shortDescriptions.length > 0;
        this.results.shortDescriptionCount = shortDescriptions.length;
        
        console.log(`Text lengths: ${JSON.stringify(textLengths)}`);
        console.log(`Found ${shortDescriptions.length} suspiciously short descriptions.`);
        
        return this.results.hasShortDescriptions ? 'warning' : 'success';
      }
    },
    
    'success': {
      execute: function() {
        console.log('=== VERIFICATION SUCCESSFUL ===');
        console.log('All checks passed. Descriptions are properly displayed.');
        
        return 'complete';
      }
    },
    
    'warning': {
      execute: function() {
        console.log('=== VERIFICATION PASSED WITH WARNINGS ===');
        console.log('Core checks passed, but some descriptions may be shorter than expected.');
        console.log('This could be normal if some performances genuinely have short descriptions.');
        
        return 'complete';
      }
    },
    
    'failure': {
      execute: function() {
        console.log('=== VERIFICATION FAILED ===');
        console.log('Some checks did not pass. The fix may not be complete.');
        
        // Determine which check failed
        if (!this.results.descriptionsExist) {
          console.error('No description elements found on the page.');
        } else if (this.results.hasCollapsedClass) {
          console.error(`${this.results.collapsedCount} descriptions still have the collapsed class.`);
        } else if (this.results.hasReadMoreButtons) {
          console.error(`${this.results.readMoreButtonCount} Read More buttons still present.`);
        } else if (this.results.hasTruncatedText) {
          console.error(`${this.results.truncatedCount} descriptions still have truncated text.`);
        }
        
        return 'complete';
      }
    },
    
    'complete': {
      execute: function() {
        console.log('Verification complete. Final results:', this.results);
        return 'complete';
      }
    }
  },
  
  // Run the state machine
  run: function() {
    let nextState = this.currentState;
    
    // Continue until we reach a terminal state
    while (nextState !== 'complete') {
      this.currentState = nextState;
      nextState = this.states[this.currentState].execute.call(this);
    }
    
    return this.results;
  }
};

// Self-executing function to run the verification
(() => {
  // Wait a short time to ensure the page is fully loaded
  setTimeout(() => {
    const results = VerificationStateMachine.run();
    
    // Make results available globally
    window.verificationResults = results;
    
    // Return a simple summary for quick reference
    return {
      success: !results.hasCollapsedClass && !results.hasReadMoreButtons && !results.hasTruncatedText,
      warnings: results.hasShortDescriptions,
      details: results
    };
  }, 500);
})();
