/**
 * Charts for the Feedback Management System dashboards
 * Using Chart.js for data visualization
 */

// Store chart instances for later updates
let categoryChart = null;
let sentimentChart = null;
let trendChart = null;
let ratingDistributionChart = null;
let sentimentTrendChart = null;
let sentimentRatioChart = null;

document.addEventListener('DOMContentLoaded', function() {
    initializeCharts();
});

/**
 * Initialize all dashboard charts
 */
function initializeCharts() {
    // Check if we're on the staff dashboard page
    const categoryChartElement = document.getElementById('categoryRatingsChart');
    const sentimentChartElement = document.getElementById('sentimentDistributionChart');
    const trendChartElement = document.getElementById('feedbackTrendChart');
    const ratingDistributionElement = document.getElementById('ratingDistributionChart');
    const sentimentTrendElement = document.getElementById('sentimentTrendChart');
    const sentimentRatioElement = document.getElementById('sentimentRatioChart');
    
    if (categoryChartElement) {
        initializeCategoryChart(categoryChartElement);
    }
    
    if (sentimentChartElement) {
        initializeSentimentChart(sentimentChartElement);
    }
    
    if (trendChartElement) {
        initializeTrendChart(trendChartElement);
    }
    
    if (ratingDistributionElement) {
        initializeRatingDistributionChart(ratingDistributionElement);
    }
    
    if (sentimentTrendElement) {
        initializeSentimentTrendChart(sentimentTrendElement);
    }
    
    if (sentimentRatioElement) {
        initializeSentimentRatioChart(sentimentRatioElement);
    }
    
    // Load initial data
    if (categoryChartElement || sentimentChartElement || trendChartElement) {
        loadAnalyticsData();
    }
    
    // Load sentiment trends data
    if (sentimentTrendElement || sentimentRatioElement) {
        loadSentimentTrends();
    }
    
    // Load AI suggestions
    if (document.getElementById('aiSuggestionsContent')) {
        loadAiSuggestions();
    }
}

/**
 * Initialize category ratings bar chart
 */
function initializeCategoryChart(chartElement) {
    const ctx = chartElement.getContext('2d');
    
    // Define color schemes for main categories and subcategories
    const categoryColors = {
        background: [
            'rgba(153, 102, 255, 0.6)', // Purple
            'rgba(54, 162, 235, 0.6)',  // Blue
            'rgba(20, 184, 166, 0.6)',  // Teal
            'rgba(255, 159, 64, 0.6)',  // Orange
            'rgba(255, 99, 132, 0.6)',  // Red
            'rgba(75, 192, 192, 0.6)',  // Green
            'rgba(102, 16, 242, 0.6)',  // Indigo
            'rgba(108, 117, 125, 0.6)'  // Gray
        ],
        border: [
            'rgba(153, 102, 255, 1)',
            'rgba(54, 162, 235, 1)',
            'rgba(20, 184, 166, 1)',
            'rgba(255, 159, 64, 1)',
            'rgba(255, 99, 132, 1)',
            'rgba(75, 192, 192, 1)',
            'rgba(102, 16, 242, 1)',
            'rgba(108, 117, 125, 1)'
        ]
    };
    
    const subcategoryColors = {
        background: [
            'rgba(153, 102, 255, 0.3)', // Purple (lighter)
            'rgba(54, 162, 235, 0.3)',  // Blue (lighter)
            'rgba(20, 184, 166, 0.3)',  // Teal (lighter)
            'rgba(255, 159, 64, 0.3)',  // Orange (lighter)
            'rgba(255, 99, 132, 0.3)',  // Red (lighter)
            'rgba(75, 192, 192, 0.3)',  // Green (lighter)
            'rgba(102, 16, 242, 0.3)',  // Indigo (lighter)
            'rgba(108, 117, 125, 0.3)'  // Gray (lighter)
        ],
        border: [
            'rgba(153, 102, 255, 0.8)',
            'rgba(54, 162, 235, 0.8)',
            'rgba(20, 184, 166, 0.8)',
            'rgba(255, 159, 64, 0.8)',
            'rgba(255, 99, 132, 0.8)',
            'rgba(75, 192, 192, 0.8)',
            'rgba(102, 16, 242, 0.8)',
            'rgba(108, 117, 125, 0.8)'
        ]
    };
    
    categoryChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: [], // Will be populated with categories and subcategories
            datasets: [{
                label: 'Average Rating',
                data: [], // Will be populated with ratings
                backgroundColor: [], // Will be dynamically assigned
                borderColor: [], // Will be dynamically assigned
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 5,
                    ticks: {
                        stepSize: 1
                    },
                    title: {
                        display: true,
                        text: 'Average Rating (1-5)'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Categories & Questions'
                    },
                    ticks: {
                        callback: function(value, index, ticks) {
                            const label = this.getLabelForValue(value);
                            
                            // For subcategories (questions), show indented label
                            if (label && label.startsWith('  -')) {
                                return label;
                            }
                            
                            // For main categories, make them bold
                            return label;
                        }
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                },
                title: {
                    display: true,
                    text: 'Average Rating by Category & Question',
                    font: {
                        size: 16
                    }
                },
                tooltip: {
                    callbacks: {
                        title: function(context) {
                            return context[0].label;
                        },
                        label: function(context) {
                            const item = context.raw;
                            if (typeof item === 'object' && item.value !== undefined) {
                                // Enhanced data format with count
                                const ratingText = `Rating: ${item.value.toFixed(1)} / 5`;
                                const countText = `Responses: ${item.count || 0}`;
                                return [ratingText, countText];
                            } else {
                                // Legacy format
                                const value = typeof item === 'object' ? item.value : item;
                                return `Average Rating: ${(value || 0).toFixed(2)}`;
                            }
                        },
                        afterLabel: function(context) {
                            const item = context.raw;
                            if (typeof item === 'object' && item.isCategory === false) {
                                return 'Question level rating';
                            }
                            return null;
                        }
                    }
                }
            }
        }
    });
}

/**
 * Initialize sentiment distribution pie chart
 */
function initializeSentimentChart(chartElement) {
    const ctx = chartElement.getContext('2d');
    
    sentimentChart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: ['Positive', 'Neutral', 'Negative'],
            datasets: [{
                data: [0, 0, 0], // Will be populated
                backgroundColor: [
                    'rgba(75, 192, 192, 0.6)', // Green for positive
                    'rgba(255, 205, 86, 0.6)', // Yellow for neutral
                    'rgba(255, 99, 132, 0.6)'  // Red for negative
                ],
                borderColor: [
                    'rgba(75, 192, 192, 1)',
                    'rgba(255, 205, 86, 1)',
                    'rgba(255, 99, 132, 1)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right'
                },
                title: {
                    display: true,
                    text: 'Sentiment Distribution',
                    font: {
                        size: 16
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.raw || 0;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = total > 0 ? Math.round((value / total) * 100) : 0;
                            return `${label}: ${value} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

/**
 * Initialize feedback trend line chart
 */
function initializeTrendChart(chartElement) {
    const ctx = chartElement.getContext('2d');
    
    trendChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [], // Will be populated with weeks/dates
            datasets: [{
                label: 'Feedback Count',
                data: [], // Will be populated
                fill: true,
                backgroundColor: 'rgba(54, 162, 235, 0.2)',
                borderColor: 'rgba(54, 162, 235, 1)',
                tension: 0.4,
                pointBackgroundColor: 'rgba(54, 162, 235, 1)',
                pointBorderColor: '#fff',
                pointHoverBackgroundColor: '#fff',
                pointHoverBorderColor: 'rgba(54, 162, 235, 1)'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Number of Feedback'
                    },
                    ticks: {
                        stepSize: 1
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Week'
                    }
                }
            },
            plugins: {
                title: {
                    display: true,
                    text: 'Feedback Trend',
                    font: {
                        size: 16
                    }
                },
                tooltip: {
                    callbacks: {
                        title: function(context) {
                            return `Week ${context[0].label}`;
                        }
                    }
                }
            }
        }
    });
}

/**
 * Initialize rating distribution chart
 */
function initializeRatingDistributionChart(chartElement) {
    const ctx = chartElement.getContext('2d');
    
    // Get the data from the data attribute
    const dataString = chartElement.getAttribute('data-ratings');
    let data = [0, 0, 0, 0, 0];
    
    if (dataString) {
        try {
            data = JSON.parse(dataString);
        } catch (e) {
            console.error('Error parsing rating distribution data:', e);
        }
    }
    
    ratingDistributionChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['1 ★', '2 ★', '3 ★', '4 ★', '5 ★'],
            datasets: [{
                label: 'Number of Ratings',
                data: data,
                backgroundColor: [
                    'rgba(255, 99, 132, 0.6)',
                    'rgba(255, 159, 64, 0.6)',
                    'rgba(255, 205, 86, 0.6)',
                    'rgba(75, 192, 192, 0.6)',
                    'rgba(54, 162, 235, 0.6)'
                ],
                borderColor: [
                    'rgba(255, 99, 132, 1)',
                    'rgba(255, 159, 64, 1)',
                    'rgba(255, 205, 86, 1)',
                    'rgba(75, 192, 192, 1)',
                    'rgba(54, 162, 235, 1)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Number of Ratings'
                    },
                    ticks: {
                        stepSize: 1
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Rating Value'
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                },
                title: {
                    display: true,
                    text: 'Rating Distribution',
                    font: {
                        size: 16
                    }
                }
            }
        }
    });
}

/**
 * Load analytics data via AJAX
 */
function loadAnalyticsData() {
    // Get filter values
    const days = document.getElementById('daysFilter')?.value || 30;
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
            
            // Set date filter values if they were returned
            if (data.filters) {
                if (document.getElementById('fromDateFilter') && !document.getElementById('fromDateFilter').value) {
                    document.getElementById('fromDateFilter').value = data.filters.from_date;
                }
                if (document.getElementById('toDateFilter') && !document.getElementById('toDateFilter').value) {
                    document.getElementById('toDateFilter').value = data.filters.to_date;
                }
            }
            
            // Update charts with retrieved data
            if (categoryChart) {
                updateCategoryChart(data.chart_data || data.avg_ratings);
            }
            
            if (sentimentChart) {
                updateSentimentChart(data.sentiment_counts);
            }
            
            if (trendChart) {
                updateTrendChart(data.feedback_trend);
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
 * Update category ratings chart with new data
 */
function updateCategoryChart(chartData) {
    if (!categoryChart) return;
    
    // Handle both new format and legacy format
    if (Array.isArray(chartData)) {
        // New format with subcategories
        const labels = [];
        const data = [];
        const backgroundColors = [];
        const borderColors = [];
        
        // Define color schemes for main categories and subcategories
        const categoryColorScheme = {
            background: [
                'rgba(153, 102, 255, 0.6)', // Purple
                'rgba(54, 162, 235, 0.6)',  // Blue
                'rgba(20, 184, 166, 0.6)',  // Teal
                'rgba(255, 159, 64, 0.6)',  // Orange
                'rgba(255, 99, 132, 0.6)',  // Red
                'rgba(75, 192, 192, 0.6)',  // Green
                'rgba(102, 16, 242, 0.6)',  // Indigo
                'rgba(108, 117, 125, 0.6)'  // Gray
            ],
            border: [
                'rgba(153, 102, 255, 1)',
                'rgba(54, 162, 235, 1)',
                'rgba(20, 184, 166, 1)',
                'rgba(255, 159, 64, 1)',
                'rgba(255, 99, 132, 1)',
                'rgba(75, 192, 192, 1)',
                'rgba(102, 16, 242, 1)',
                'rgba(108, 117, 125, 1)'
            ]
        };
        
        const subcategoryColorScheme = {
            background: [
                'rgba(153, 102, 255, 0.3)', // Purple (lighter)
                'rgba(54, 162, 235, 0.3)',  // Blue (lighter)
                'rgba(20, 184, 166, 0.3)',  // Teal (lighter)
                'rgba(255, 159, 64, 0.3)',  // Orange (lighter)
                'rgba(255, 99, 132, 0.3)',  // Red (lighter)
                'rgba(75, 192, 192, 0.3)',  // Green (lighter)
                'rgba(102, 16, 242, 0.3)',  // Indigo (lighter)
                'rgba(108, 117, 125, 0.3)'  // Gray (lighter)
            ],
            border: [
                'rgba(153, 102, 255, 0.8)',
                'rgba(54, 162, 235, 0.8)',
                'rgba(20, 184, 166, 0.8)',
                'rgba(255, 159, 64, 0.8)',
                'rgba(255, 99, 132, 0.8)',
                'rgba(75, 192, 192, 0.8)',
                'rgba(102, 16, 242, 0.8)',
                'rgba(108, 117, 125, 0.8)'
            ]
        };
        
        // Track main category colors to apply the same color to their subcategories
        const categoryColorMap = {};
        let colorIndex = 0;
        
        // Process chart data
        chartData.forEach(item => {
            labels.push(item.label);
            
            // Handle different data formats
            if (typeof item === 'object' && item.value !== undefined) {
                data.push(item);
            } else {
                data.push(item);
            }
            
            // Apply appropriate colors based on whether it's a category or subcategory
            if (item.isCategory) {
                // For main categories
                const bgColor = categoryColorScheme.background[colorIndex % categoryColorScheme.background.length];
                const borderColor = categoryColorScheme.border[colorIndex % categoryColorScheme.border.length];
                
                backgroundColors.push(bgColor);
                borderColors.push(borderColor);
                
                // Store the color index for this category for its subcategories
                if (item.id) {
                    categoryColorMap[item.id] = colorIndex;
                }
                
                colorIndex++;
            } else {
                // For subcategories
                let parentColorIndex = 0;
                
                // If we have parent ID, use its color
                if (item.parentId && categoryColorMap[item.parentId] !== undefined) {
                    parentColorIndex = categoryColorMap[item.parentId];
                }
                
                const bgColor = subcategoryColorScheme.background[parentColorIndex % subcategoryColorScheme.background.length];
                const borderColor = subcategoryColorScheme.border[parentColorIndex % subcategoryColorScheme.border.length];
                
                backgroundColors.push(bgColor);
                borderColors.push(borderColor);
            }
        });
        
        // Update chart with new data and colors
        categoryChart.data.labels = labels;
        categoryChart.data.datasets[0].data = data;
        categoryChart.data.datasets[0].backgroundColor = backgroundColors;
        categoryChart.data.datasets[0].borderColor = borderColors;
    } else {
        // Legacy format (simple object of category -> rating)
        const labels = Object.keys(chartData);
        const data = Object.values(chartData);
        
        categoryChart.data.labels = labels;
        categoryChart.data.datasets[0].data = data;
    }
    
    categoryChart.update();
}

/**
 * Update sentiment distribution chart with new data
 */
function updateSentimentChart(sentimentCounts) {
    if (!sentimentChart) return;
    
    const positiveCount = sentimentCounts.positive || 0;
    const neutralCount = sentimentCounts.neutral || 0;
    const negativeCount = sentimentCounts.negative || 0;
    
    sentimentChart.data.datasets[0].data = [positiveCount, neutralCount, negativeCount];
    sentimentChart.update();
}

/**
 * Load and display areas for improvement (for CC dashboard)
 */
function loadAreasForImprovement() {
    fetch('/api/areas_of_improvement')
        .then(response => response.json())
        .then(data => {
            const improvementAreas = data.areas || [];
            const container = document.getElementById('improvementAreasContainer');
            
            // Clear previous content
            if (container) {
                container.innerHTML = '';
                
                if (improvementAreas.length === 0) {
                    container.innerHTML = `
                        <div class="alert alert-info">
                            <i class="fas fa-info-circle me-2"></i>
                            No areas for improvement detected in recent feedback.
                        </div>
                    `;
                    return;
                }
                
                // Create list of improvement areas
                const list = document.createElement('div');
                list.className = 'list-group';
                
                improvementAreas.forEach(area => {
                    const item = document.createElement('div');
                    item.className = 'list-group-item';
                    
                    // Create badge for sentiment
                    let badgeClass = 'bg-danger';
                    if (area.avg_sentiment > 0.3) {
                        badgeClass = 'bg-warning';
                    }
                    
                    // Format comments
                    let commentsHtml = '';
                    if (area.comments && area.comments.length > 0) {
                        commentsHtml = `
                            <small class="d-block mt-2 text-muted">
                                <strong>Sample feedback:</strong>
                                <ul class="mb-0 small">
                                    ${area.comments.map(comment => `<li>"${comment}"</li>`).join('')}
                                </ul>
                            </small>
                        `;
                    }
                    
                    item.innerHTML = `
                        <div class="d-flex justify-content-between align-items-center">
                            <h6 class="mb-1">${area.category}</h6>
                            <span class="badge ${badgeClass}">${area.count} issues</span>
                        </div>
                        ${commentsHtml}
                    `;
                    
                    list.appendChild(item);
                });
                
                container.appendChild(list);
            }
        })
        .catch(error => {
            console.error('Error loading improvement areas:', error);
        });
}

/**
 * Update feedback trend chart with new data
 */
function updateTrendChart(trendData) {
    if (!trendChart) return;
    
    const labels = Object.keys(trendData);
    const data = Object.values(trendData);
    
    // Format week labels (YYYY-WW) to more readable format
    const formattedLabels = labels.map(weekStr => {
        const parts = weekStr.split('-');
        return `${parts[0]}-W${parts[1]}`;
    });
    
    trendChart.data.labels = formattedLabels;
    trendChart.data.datasets[0].data = data;
    trendChart.update();
}

/**
 * Load and display areas for improvement (for CC dashboard)
 */
function loadAreasForImprovement() {
    const days = document.getElementById('dateRangeFilter')?.value || 30;
    const areasContainer = document.getElementById('areasForImprovement');
    
    if (!areasContainer) return;
    
    fetch(`/areas_of_improvement?days=${days}`)
        .then(response => response.json())
        .then(data => {
            let html = '';
            
            // Display low-rated categories
            if (data.low_rated_categories && data.low_rated_categories.length > 0) {
                html += '<h6 class="fw-bold mb-3">Low-Rated Categories:</h6>';
                html += '<ul class="list-group list-group-flush mb-4">';
                
                data.low_rated_categories.forEach(category => {
                    const ratingStars = '★'.repeat(Math.round(category.avg_rating)) + 
                                       '☆'.repeat(5 - Math.round(category.avg_rating));
                    
                    html += `<li class="list-group-item d-flex justify-content-between align-items-center">
                        <span>${category.name}</span>
                        <span class="text-warning">${ratingStars} (${category.avg_rating.toFixed(2)})</span>
                    </li>`;
                });
                
                html += '</ul>';
            }
            
            // Display negative aspects
            if (data.negative_aspects && data.negative_aspects.length > 0) {
                html += '<h6 class="fw-bold mb-3">Most Mentioned Issues:</h6>';
                html += '<ul class="list-group list-group-flush">';
                
                data.negative_aspects.forEach(aspect => {
                    html += `<li class="list-group-item d-flex justify-content-between align-items-center">
                        <span>${aspect.aspect}</span>
                        <span class="badge bg-danger rounded-pill">${aspect.count} mentions</span>
                    </li>`;
                });
                
                html += '</ul>';
            }
            
            // If no data
            if ((!data.low_rated_categories || data.low_rated_categories.length === 0) && 
                (!data.negative_aspects || data.negative_aspects.length === 0)) {
                html = `<div class="text-center py-4">
                    <i class="fas fa-check-circle fa-3x mb-3 text-success"></i>
                    <p class="text-muted">No improvement areas identified in the selected time period.</p>
                </div>`;
            }
            
            areasContainer.innerHTML = html;
        })
        .catch(error => {
            console.error('Error loading areas for improvement:', error);
            areasContainer.innerHTML = `<div class="alert alert-danger">
                <i class="fas fa-exclamation-triangle me-2"></i>
                Error loading improvement areas data.
            </div>`;
        });
}

// Add event listener for document ready to initialize areas for improvement
document.addEventListener('DOMContentLoaded', function() {
    // Initialize charts (already being called)
    
    // Load areas for improvement if on staff dashboard
    if (document.getElementById('areasForImprovement')) {
        loadAreasForImprovement();
        
        // Update when date range changes
        const dateRangeFilter = document.getElementById('dateRangeFilter');
        if (dateRangeFilter) {
            dateRangeFilter.addEventListener('change', function() {
                loadAreasForImprovement();
            });
        }
    }
    
    // Add download report button event listener
    const downloadBtn = document.getElementById('downloadReportBtn');
    if (downloadBtn) {
        downloadBtn.addEventListener('click', function(e) {
            e.preventDefault();
            const days = document.getElementById('dateRangeFilter')?.value || 30;
            window.location.href = `/download_report?days=${days}`;
        });
    }
});

/**
 * Initialize sentiment trend chart
 */
function initializeSentimentTrendChart(chartElement) {
    const ctx = chartElement.getContext('2d');
    
    sentimentTrendChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: [], // Will be populated with time periods
            datasets: [
                {
                    label: 'Positive',
                    data: [], // Will be populated with positive sentiment counts
                    backgroundColor: 'rgba(75, 192, 192, 0.6)', // Green
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 1
                },
                {
                    label: 'Neutral',
                    data: [], // Will be populated with neutral sentiment counts
                    backgroundColor: 'rgba(255, 205, 86, 0.6)', // Yellow
                    borderColor: 'rgba(255, 205, 86, 1)',
                    borderWidth: 1
                },
                {
                    label: 'Negative',
                    data: [], // Will be populated with negative sentiment counts
                    backgroundColor: 'rgba(255, 99, 132, 0.6)', // Red
                    borderColor: 'rgba(255, 99, 132, 1)',
                    borderWidth: 1
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    stacked: true,
                    title: {
                        display: true,
                        text: 'Time Period'
                    }
                },
                y: {
                    stacked: true,
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Feedback Count'
                    },
                    ticks: {
                        stepSize: 1
                    }
                }
            },
            plugins: {
                title: {
                    display: true,
                    text: 'Sentiment Distribution Over Time',
                    font: {
                        size: 16
                    }
                },
                tooltip: {
                    mode: 'index',
                    intersect: false
                }
            }
        }
    });
}

/**
 * Initialize sentiment ratio chart
 */
function initializeSentimentRatioChart(chartElement) {
    const ctx = chartElement.getContext('2d');
    
    sentimentRatioChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [], // Will be populated with time periods
            datasets: [
                {
                    label: 'Positive %',
                    data: [], // Will be populated with positive sentiment percentages
                    backgroundColor: 'rgba(75, 192, 192, 0.1)',
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4
                },
                {
                    label: 'Neutral %',
                    data: [], // Will be populated with neutral sentiment percentages
                    backgroundColor: 'rgba(255, 205, 86, 0.1)',
                    borderColor: 'rgba(255, 205, 86, 1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4
                },
                {
                    label: 'Negative %',
                    data: [], // Will be populated with negative sentiment percentages
                    backgroundColor: 'rgba(255, 99, 132, 0.1)',
                    borderColor: 'rgba(255, 99, 132, 1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    title: {
                        display: true,
                        text: 'Percentage (%)'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Time Period'
                    }
                }
            },
            plugins: {
                title: {
                    display: true,
                    text: 'Sentiment Ratio Trends',
                    font: {
                        size: 16
                    }
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    callbacks: {
                        label: function(context) {
                            return `${context.dataset.label}: ${context.raw.toFixed(1)}%`;
                        }
                    }
                }
            }
        }
    });
}

/**
 * Load sentiment trends data via AJAX
 */
function loadSentimentTrends() {
    const days = document.getElementById('dateRangeFilter')?.value || 365;
    
    fetch(`/sentiment_trends?days=${days}`)
        .then(response => response.json())
        .then(data => {
            updateSentimentTrendCharts(data);
        })
        .catch(error => {
            console.error('Error loading sentiment trends data:', error);
        });
}

/**
 * Update sentiment trend charts with new data
 */
function updateSentimentTrendCharts(data) {
    if (!sentimentTrendChart || !sentimentRatioChart) return;
    
    const trendData = data.trend_data || [];
    const ratioData = data.sentiment_ratio || [];
    
    // Update sentiment trend chart
    if (sentimentTrendChart) {
        const labels = trendData.map(item => item[0]); // Period labels
        const positiveData = trendData.map(item => item[1].positive || 0);
        const neutralData = trendData.map(item => item[1].neutral || 0);
        const negativeData = trendData.map(item => item[1].negative || 0);
        
        sentimentTrendChart.data.labels = labels;
        sentimentTrendChart.data.datasets[0].data = positiveData;
        sentimentTrendChart.data.datasets[1].data = neutralData;
        sentimentTrendChart.data.datasets[2].data = negativeData;
        sentimentTrendChart.update();
    }
    
    // Update sentiment ratio chart
    if (sentimentRatioChart) {
        const labels = ratioData.map(item => item[0]); // Period labels
        const positiveRatios = ratioData.map(item => item[1].positive_ratio || 0);
        const neutralRatios = ratioData.map(item => item[1].neutral_ratio || 0);
        const negativeRatios = ratioData.map(item => item[1].negative_ratio || 0);
        
        sentimentRatioChart.data.labels = labels;
        sentimentRatioChart.data.datasets[0].data = positiveRatios;
        sentimentRatioChart.data.datasets[1].data = neutralRatios;
        sentimentRatioChart.data.datasets[2].data = negativeRatios;
        sentimentRatioChart.update();
    }
}

/**
 * Load AI-generated improvement suggestions
 */
function loadAiSuggestions() {
    const days = document.getElementById('dateRangeFilter')?.value || 90;
    const suggestionsContainer = document.getElementById('aiSuggestionsContent');
    
    if (!suggestionsContainer) return;
    
    fetch(`/ai_feedback_suggestions?days=${days}`)
        .then(response => response.json())
        .then(data => {
            let html = '';
            
            if (data.suggestions && data.suggestions.length > 0) {
                html = '<ul class="list-group list-group-flush">';
                
                data.suggestions.forEach((suggestion, index) => {
                    // Add different background colors based on relevance
                    let bgClass = '';
                    if (index === 0) bgClass = 'list-group-item-warning';
                    else if (index === 1) bgClass = 'list-group-item-light';
                    
                    html += `<li class="list-group-item ${bgClass}">
                        <h6 class="mb-1"><i class="fas fa-lightbulb text-warning me-2"></i> ${suggestion.theme}</h6>
                        <p class="mb-0">${suggestion.suggestion}</p>
                    </li>`;
                });
                
                html += '</ul>';
            } else {
                html = `<div class="text-center py-4">
                    <i class="fas fa-smile fa-3x mb-3 text-success"></i>
                    <p class="text-muted">No specific improvement suggestions at this time.</p>
                </div>`;
            }
            
            suggestionsContainer.innerHTML = html;
        })
        .catch(error => {
            console.error('Error loading AI suggestions:', error);
            suggestionsContainer.innerHTML = `<div class="alert alert-danger">
                <i class="fas fa-exclamation-triangle me-2"></i>
                Error loading AI suggestions.
            </div>`;
        });
}
