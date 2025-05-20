from flask import Flask, render_template, jsonify
import os
import json
from datetime import datetime, timedelta
import random

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('test_features.html')

@app.route('/sentiment_trends_test')
def sentiment_trends_test():
    """Test endpoint for sentiment trends data"""
    # Generate test data for demonstration
    months = []
    trend_data = []
    ratio_data = []
    
    # Generate data for the last 12 months
    for i in range(12):
        date = datetime.now() - timedelta(days=30 * i)
        month = date.strftime('%Y-%m')
        months.append(month)
        
        # Random counts for sentiments
        positive = random.randint(10, 50)
        neutral = random.randint(5, 30)
        negative = random.randint(1, 20)
        total = positive + neutral + negative
        
        # Add to trend data
        trend_data.append((month, {
            'positive': positive,
            'neutral': neutral,
            'negative': negative
        }))
        
        # Calculate ratios
        ratio_data.append((month, {
            'positive_ratio': round(positive / total * 100, 1),
            'neutral_ratio': round(neutral / total * 100, 1),
            'negative_ratio': round(negative / total * 100, 1),
            'total': total
        }))
    
    # Return results
    return jsonify({
        'trend_data': trend_data,
        'sentiment_ratio': ratio_data,
        'period': 'month',
        'days': 365
    })

@app.route('/ai_suggestions_test')
def ai_suggestions_test():
    """Test endpoint for AI suggestions data"""
    # Sample suggestions
    suggestions = [
        {
            'theme': 'Course Content',
            'suggestion': 'Consider simplifying complex topics and providing more scaffolded learning materials.',
            'relevance': 5
        },
        {
            'theme': 'Teaching Approaches',
            'suggestion': 'Incorporate more interactive activities and real-world applications to increase engagement.',
            'relevance': 3
        },
        {
            'theme': 'Assessment Methods',
            'suggestion': 'Consider providing additional practice opportunities and more graduated difficulty levels.',
            'relevance': 2
        }
    ]
    
    return jsonify({
        'suggestions': suggestions,
        'feedback_count': 42,
        'days': 90
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)