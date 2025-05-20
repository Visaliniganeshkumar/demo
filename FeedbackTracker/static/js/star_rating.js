/**
 * Star Rating Component for Feedback Form
 */

document.addEventListener('DOMContentLoaded', function() {
    initializeStarRatings();
});

/**
 * Initialize all star rating controls
 */
function initializeStarRatings() {
    const starRatingContainers = document.querySelectorAll('.star-rating');
    
    starRatingContainers.forEach(container => {
        const stars = container.querySelectorAll('input[type="radio"]');
        const ratingValueDisplay = document.getElementById(container.dataset.displayId);
        
        // Set initial value if a star is already selected
        updateRatingDisplay(container, ratingValueDisplay);
        
        // Add click event listeners to stars
        stars.forEach(star => {
            star.addEventListener('change', function() {
                // Apply animation to clicked star
                this.nextElementSibling.classList.add('star-checked');
                
                // Update display value
                updateRatingDisplay(container, ratingValueDisplay);
                
                // Trigger custom event for any listeners
                const event = new CustomEvent('rating-changed', { 
                    detail: { 
                        containerId: container.id,
                        questionId: container.dataset.questionId,
                        value: this.value 
                    } 
                });
                container.dispatchEvent(event);
            });
            
            // Add hover effect
            star.nextElementSibling.addEventListener('mouseenter', function() {
                // Get all stars after this one
                let sibling = this;
                let siblings = [];
                while (sibling) {
                    siblings.push(sibling);
                    sibling = sibling.nextElementSibling;
                }
                
                // Add hover class to stars
                siblings.forEach(s => {
                    s.classList.add('star-hover');
                });
            });
            
            star.nextElementSibling.addEventListener('mouseleave', function() {
                // Get all stars after this one
                let sibling = this;
                let siblings = [];
                while (sibling) {
                    siblings.push(sibling);
                    sibling = sibling.nextElementSibling;
                }
                
                // Remove hover class from stars
                siblings.forEach(s => {
                    s.classList.remove('star-hover');
                });
            });
        });
    });
}

/**
 * Update the rating display value
 */
function updateRatingDisplay(container, displayElement) {
    if (!displayElement) return;
    
    const selectedStar = container.querySelector('input[type="radio"]:checked');
    
    if (selectedStar) {
        const ratingValue = selectedStar.value;
        displayElement.textContent = ratingValue;
        
        // Set a descriptive text based on rating
        const descriptions = [
            '',  // No description for 0
            'Poor',
            'Fair',
            'Good',
            'Very Good',
            'Excellent'
        ];
        
        // Find any description element related to this rating
        const descriptionElement = document.getElementById(container.dataset.descriptionId);
        if (descriptionElement) {
            descriptionElement.textContent = descriptions[ratingValue] || '';
        }
    } else {
        displayElement.textContent = '0';
    }
}

/**
 * Reset all star ratings in a form
 */
function resetStarRatings(formId) {
    const form = document.getElementById(formId);
    if (!form) return;
    
    const starContainers = form.querySelectorAll('.star-rating');
    
    starContainers.forEach(container => {
        // Uncheck all stars
        const stars = container.querySelectorAll('input[type="radio"]');
        stars.forEach(star => {
            star.checked = false;
        });
        
        // Update display
        const displayId = container.dataset.displayId;
        if (displayId) {
            const displayElement = document.getElementById(displayId);
            updateRatingDisplay(container, displayElement);
        }
    });
}

/**
 * Set a specific rating value programmatically
 */
function setRatingValue(containerId, value) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    const stars = container.querySelectorAll('input[type="radio"]');
    
    stars.forEach(star => {
        if (parseInt(star.value) === parseInt(value)) {
            star.checked = true;
            
            // Update display
            const displayId = container.dataset.displayId;
            if (displayId) {
                const displayElement = document.getElementById(displayId);
                updateRatingDisplay(container, displayElement);
            }
        }
    });
}
