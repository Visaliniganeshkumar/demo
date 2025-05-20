// Dark mode functionality
function toggleDarkMode() {
    document.body.classList.toggle('dark-mode');
    const isDarkMode = document.body.classList.contains('dark-mode');
    localStorage.setItem('darkMode', isDarkMode);

    // Update icon
    const icon = document.querySelector('#darkModeToggle i');
    icon.className = isDarkMode ? 'fas fa-sun' : 'fas fa-moon';
}

// Initialize dark mode from localStorage
function initializeDarkMode() {
    const isDarkMode = localStorage.getItem('darkMode') === 'true';
    if (isDarkMode) {
        document.body.classList.add('dark-mode');
        const icon = document.querySelector('#darkModeToggle i');
        if (icon) icon.className = 'fas fa-sun';
    }
}

document.addEventListener('DOMContentLoaded', function() {
    initializeDarkMode();
    const feedbackForm = document.getElementById('feedbackForm');

    if (feedbackForm) {
        // Handle form submission
        feedbackForm.addEventListener('submit', function(e) {
            const selectedCategories = document.querySelectorAll('.category-selector:checked');

            // Check if any category is selected
            if (selectedCategories.length === 0) {
                e.preventDefault();
                alert('Please select at least one category to provide feedback.');
                return;
            }

            // Validate selected categories have ratings
            let isValid = true;
            selectedCategories.forEach(category => {
                const categoryId = category.value;
                const ratings = document.querySelectorAll(`input[name^="rating_"][name*="${categoryId}"]:checked`);
                if (ratings.length === 0) {
                    isValid = false;
                }
            });

            if (!isValid) {
                e.preventDefault();
                alert('Please provide ratings for all selected categories.');
                return;
            }
        });

        // Show/hide category sections based on selection
        document.querySelectorAll('.category-selector').forEach(checkbox => {
            checkbox.addEventListener('change', function() {
                const categoryName = this.dataset.categoryName;
                const categoryCard = document.querySelector(`.category-${categoryName}`);

                if (categoryCard) {
                    if (this.checked) {
                        categoryCard.style.display = 'block';
                        categoryCard.scrollIntoView({ behavior: 'smooth', block: 'start' });
                    } else {
                        categoryCard.style.display = 'none';
                    }
                }
            });
        });
    }
});

document.addEventListener('DOMContentLoaded', function() {
    // Handle showing/hiding individual category submit buttons
    const categorySelectors = document.querySelectorAll('.category-selector');
    categorySelectors.forEach(selector => {
        selector.addEventListener('change', function() {
            const categoryName = this.dataset.categoryName;
            const submitBtn = document.querySelector(`.category-${categoryName}`);
            if (submitBtn) {
                submitBtn.style.display = this.checked ? 'block' : 'none';
            }
        });
    });
    // Initialize tooltips
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));

    // Initialize popovers
    const popoverTriggerList = document.querySelectorAll('[data-bs-toggle="popover"]');
    const popoverList = [...popoverTriggerList].map(popoverTriggerEl => new bootstrap.Popover(popoverTriggerEl));

    // Handle alert dismissal with fade out
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(alert => {
        const closeBtn = alert.querySelector('.btn-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', function() {
                alert.style.transition = 'opacity 0.5s ease';
                alert.style.opacity = '0';
                setTimeout(() => {
                    alert.style.display = 'none';
                }, 500);
            });
        }
    });

    // Handle message read status
    const unreadMessages = document.querySelectorAll('.message-unread');
    unreadMessages.forEach(message => {
        message.addEventListener('click', function() {
            const messageId = this.getAttribute('data-message-id');
            if (messageId) {
                markMessageAsRead(messageId);
            }
        });
    });

    // Handle form submission animation
    const feedbackForm = document.getElementById('feedbackForm');
    if (feedbackForm) {
        feedbackForm.addEventListener('submit', function(e) {
            // Don't add animation if form validation fails
            if (!this.checkValidity()) {
                return;
            }

            // Add a loading spinner to submit button
            const submitBtn = this.querySelector('button[type="submit"]');
            const originalBtnText = submitBtn.innerHTML;
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Submitting...';

            // We're not preventing default form submission here
            // The form will submit normally, and the page will reload
        });
    }

    // Handle date range filter for staff dashboard
    const dateRangeFilter = document.getElementById('dateRangeFilter');
    if (dateRangeFilter) {
        dateRangeFilter.addEventListener('change', function() {
            const days = this.value;
            window.location.href = `/dashboard/staff?days=${days}`;
        });
    }

    // Initialize dashboard data refresh timer
    initializeDashboardRefresh();

    // Handle forwarding selection in response form
    const actionSelect = document.getElementById('actionSelect');
    if (actionSelect) {
        const forwardToDiv = document.getElementById('forwardToDiv');
        actionSelect.addEventListener('change', function() {
            if (this.value === 'forward') {
                forwardToDiv.classList.remove('d-none');
                document.getElementById('forwardTo').setAttribute('required', 'required');
            } else {
                forwardToDiv.classList.add('d-none');
                document.getElementById('forwardTo').removeAttribute('required');
            }
        });
    }

    // Handle anonymous feedback toggle
    const anonymousCheckbox = document.getElementById('anonymousFeedback');
    if (anonymousCheckbox) {
        const anonymousWarning = document.getElementById('anonymousWarning');
        anonymousCheckbox.addEventListener('change', function() {
            if (this.checked) {
                anonymousWarning.classList.remove('d-none');
            } else {
                anonymousWarning.classList.add('d-none');
            }
        });
    }
});

/**
 * Function to mark a message as read via AJAX
 */
function markMessageAsRead(messageId) {
    fetch(`/api/mark_message_read/${messageId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Remove unread styling
            const messageElement = document.querySelector(`.message-unread[data-message-id="${messageId}"]`);
            if (messageElement) {
                messageElement.classList.remove('message-unread');
            }

            // Update unread count if displayed
            const unreadBadge = document.getElementById('unreadMessageCount');
            if (unreadBadge) {
                const currentCount = parseInt(unreadBadge.textContent);
                if (currentCount > 0) {
                    unreadBadge.textContent = currentCount - 1;
                    if (currentCount - 1 === 0) {
                        unreadBadge.classList.add('d-none');
                    }
                }
            }
        }
    })
    .catch(error => {
        console.error('Error marking message as read:', error);
    });
}

/**
 * Function to refresh dashboard data periodically
 */
function initializeDashboardRefresh() {
    const analyticsCharts = document.getElementById('analyticsCharts');
    if (analyticsCharts) {
        // Refresh analytics data every 5 minutes
        setInterval(() => {
            refreshAnalyticsData();
        }, 5 * 60 * 1000);
    }
}

/**
 * Function to refresh analytics data via AJAX
 */
function refreshAnalyticsData() {
    // Reset filters
    const fromDateFilter = document.getElementById('fromDateFilter');
    const toDateFilter = document.getElementById('toDateFilter');
    const categoryFilter = document.getElementById('categoryFilter');

    if (fromDateFilter) fromDateFilter.value = '';
    if (toDateFilter) toDateFilter.value = '';
    if (categoryFilter) categoryFilter.value = '';

    // Load analytics with default values (last 30 days)
    loadAnalyticsData();
}

/**
 * Load analytics data with current filter settings
 */
function loadAnalyticsData() {
    // Get filter values
    const days = 30; // Default to 30 days if date range not specified
    const fromDate = document.getElementById('fromDateFilter')?.value || '';
    const toDate = document.getElementById('toDateFilter')?.value || '';
    const category = document.getElementById('categoryFilter')?.value || '';

    // Build query parameters
    let queryParams = new URLSearchParams();
    if (fromDate && toDate) {
        queryParams.append('from_date', fromDate);
        queryParams.append('to_date', toDate);
    } else {
        queryParams.append('days', days);
    }

    if (category) {
        queryParams.append('category', category);
    }

    fetch(`/api/feedback/analytics?${queryParams.toString()}`)
        .then(response => response.json())
        .then(data => {
            // Update filter UI with available categories if present
            if (data.filters && data.filters.available_categories) {
                updateCategoryFilterOptions(data.filters.available_categories);
            }

            // Set date filter values if they were returned and not already set
            if (data.filters) {
                if (document.getElementById('fromDateFilter') && !document.getElementById('fromDateFilter').value) {
                    document.getElementById('fromDateFilter').value = data.filters.from_date;
                }
                if (document.getElementById('toDateFilter') && !document.getElementById('toDateFilter').value) {
                    document.getElementById('toDateFilter').value = data.filters.to_date;
                }
            }

            // Update charts with retrieved data
            if (window.categoryChart) {
                window.updateCategoryChart(data.chart_data || data.avg_ratings);
            }

            if (window.sentimentChart) {
                window.updateSentimentChart(data.sentiment_counts);
            }

            if (window.trendChart) {
                window.updateTrendChart(data.feedback_trend);
            }
        })
        .catch(error => {
            console.error('Error loading analytics data:', error);
        });
}

/**
 * Update category filter dropdown with available categories
 */
function updateCategoryFilterOptions(categories) {
    const categoryFilter = document.getElementById('categoryFilter');
    if (!categoryFilter) return;

    // Save current selection
    const currentValue = categoryFilter.value;

    // Clear existing options except the first "All Categories" option
    while (categoryFilter.options.length > 1) {
        categoryFilter.remove(1);
    }

    // Add category options
    categories.forEach(category => {
        const option = document.createElement('option');
        option.value = category.name;
        option.textContent = category.name;
        categoryFilter.appendChild(option);
    });

    // Restore selection if it exists in the new options
    if (currentValue) {
        categoryFilter.value = currentValue;
    }
}

/**
 * Toggle password visibility in password fields
 */
function togglePasswordVisibility(inputId, toggleBtnId) {
    const passwordInput = document.getElementById(inputId);
    const toggleBtn = document.getElementById(toggleBtnId);

    if (passwordInput.type === 'password') {
        passwordInput.type = 'text';
        toggleBtn.innerHTML = '<i class="fas fa-eye-slash"></i>';
    } else {
        passwordInput.type = 'password';
        toggleBtn.innerHTML = '<i class="fas fa-eye"></i>';
    }
}

/**
 * Function to confirm before deleting items
 */
function confirmDelete(message) {
    return confirm(message || 'Are you sure you want to delete this item?');
}
// Function to show new message notification
function showNewMessageNotification(message) {
    const notification = document.createElement('div');
    notification.className = 'new-message-notification';
    notification.innerHTML = `<i class="fas fa-envelope me-2"></i>${message}`;
    document.body.appendChild(notification);

    notification.style.display = 'block';
    setTimeout(() => {
        notification.style.opacity = '0';
        setTimeout(() => notification.remove(), 500);
    }, 3000);
}

// Check for new messages periodically
function checkNewMessages() {
    fetch('/api/check_new_messages')
        .then(response => response.json())
        .then(data => {
            if (data.new_messages > 0) {
                showNewMessageNotification(`You have ${data.new_messages} new message(s)`);
                updateUnreadCount(data.new_messages);
            }
        });
}

// Start checking for new messages every 30 seconds
setInterval(checkNewMessages, 30000);
// Quick reply functionality
function quickReply(btn, type) {
    const responseId = btn.dataset.responseId;
    let message = '';

    switch(type) {
        case 'accept':
            message = "Thank you for your feedback. I have accepted and will review it.";
            break;
        case 'review':
            message = "I am currently reviewing your feedback and will respond shortly.";
            break;
        case 'forward':
            showForwardForm(responseId);
            return;
    }

    if (message) {
        document.getElementById('response').value = message;
        document.getElementById('parent_response_id').value = responseId;
        document.getElementById('responseForm').submit();
    }
}

// Show message tracking
function showMessageTracking(messageId) {
    const trackingDiv = document.getElementById(`tracking-${messageId}`);
    if (trackingDiv) {
        trackingDiv.classList.toggle('d-none');
    }
}

// Forward message functionality 
function showForwardForm(messageId, messageText) {
    const modal = new bootstrap.Modal(document.getElementById('forwardMessageModal'));
    document.getElementById('original_message_id').value = messageId;
    document.getElementById('forward_message').value = messageText;
    modal.show();
}
// Handle reply buttons
document.addEventListener('DOMContentLoaded', function() {
    const replyModal = document.getElementById('replyModal');
    if (replyModal) {
        const replyForm = document.getElementById('replyForm');

        document.querySelectorAll('.reply-btn').forEach(button => {
            button.addEventListener('click', function() {
                const feedbackId = this.dataset.feedbackId;
                const responseId = this.dataset.responseId;

                replyForm.action = `/respond/${feedbackId}`;
                new bootstrap.Modal(replyModal).show();
            });
        });

        replyForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(this);

            fetch(this.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    bootstrap.Modal.getInstance(replyModal).hide();
                    window.location.reload();
                }
            });
        });
    }
});