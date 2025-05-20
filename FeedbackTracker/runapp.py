"""
Simplified starter script for the Feedback Management System.
This script starts the Flask application directly, bypassing gunicorn.
"""

import sys
import logging
from flask import Flask
from app import app, db
from models import User

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Print basic information
logger.info(f"Python version: {sys.version}")
logger.info(f"Starting Feedback Management System")

# Create routes for basic operation check
@app.route('/check')
def check():
    """Simple route to verify the app is running"""
    from models import User
    with app.app_context():
        users = User.query.all()
        user_list = [f"{user.username} ({user.email}, role: {user.role})" for user in users]
    
    return f"""
    <html>
    <head>
        <title>System Check</title>
        <link href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css" rel="stylesheet">
    </head>
    <body>
        <div class="container mt-5">
            <div class="alert alert-success">
                <h4>System is running!</h4>
                <p>Database connection is working. Found {len(user_list)} users.</p>
                <ul>
                    {''.join(f'<li>{user}</li>' for user in user_list)}
                </ul>
                <p>
                    <a href="/" class="btn btn-primary">Go to Login</a>
                </p>
            </div>
        </div>
    </body>
    </html>
    """

if __name__ == "__main__":
    logger.info("Starting Flask application...")
    # Start the application with debugging enabled
    app.run(host="0.0.0.0", port=5000, debug=True)