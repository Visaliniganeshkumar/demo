import os
import logging
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create a simple Flask app
app = Flask(__name__)
app.secret_key = "test_secret_key"

@app.route('/')
def home():
    return "Test app is working!"

@app.route('/test_templates')
def test_templates():
    try:
        return render_template('layout.html')
    except Exception as e:
        logger.error(f"Template error: {e}")
        return f"Template error: {str(e)}"

if __name__ == '__main__':
    # Run the app
    app.run(host='0.0.0.0', port=5000, debug=True)