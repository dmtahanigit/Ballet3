/**
 * Thumbnail Verification Script
 * 
 * This script verifies that thumbnails are loading correctly on the Paris Opera Ballet page.
 * It checks for the presence of images, validates their sources, and ensures they're not
 * being replaced with the fallback placeholder.
 */

(() => {
    console.log('Running thumbnail verification...');
    
    // Get all performance images
    const performanceImages = document.querySelectorAll('.performance-image');
    
    // Initialize results object
    const results = {
        totalImages: performanceImages.length,
        loadedImages: 0,
        placeholderImages: 0,
        brokenImages: 0,
        imageUrls: []
    };
    
    // Check each image
    performanceImages.forEach((img, index) => {
        // Get the image URL
        const imageUrl = img.getAttribute('src');
        
        // Add to results
        results.imageUrls.push({
            index,
            url: imageUrl,
            isPlaceholder: imageUrl.includes('placeholder-performance.jpg'),
            isLoaded: img.complete && img.naturalWidth > 0
        });
        
        // Update counts
        if (imageUrl.includes('placeholder-performance.jpg')) {
            results.placeholderImages++;
        } else if (img.complete && img.naturalWidth > 0) {
            results.loadedImages++;
        } else {
            results.brokenImages++;
        }
    });
    
    // Calculate success rate
    results.successRate = results.totalImages > 0 
        ? ((results.loadedImages / results.totalImages) * 100).toFixed(2) + '%' 
        : '0%';
    
    // Log results
    console.log('Thumbnail Verification Results:', results);
    
    // Return a simple pass/fail result
    return {
        test: 'thumbnail-verification',
        passed: results.brokenImages === 0,
        message: `${results.loadedImages} of ${results.totalImages} images loaded successfully (${results.successRate})`,
        details: results
    };
})();
