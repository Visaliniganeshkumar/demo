"""
Quick testing script for feedback management system
Run this directly to test the application without gunicorn
"""
import os
import sys
import logging
from app import app
from routes import initialize_database

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    logger.info("Starting quick test app...")
    
    # Print some diagnostics
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Current directory: {os.getcwd()}")
    logger.info(f"Database URL: {app.config.get('SQLALCHEMY_DATABASE_URI')}")
    
    # Initialize database within application context
    with app.app_context():
        initialize_database()
    
    # Run the app
    logger.info("Starting Flask development server")
    app.run(host='0.0.0.0', port=5000, debug=True)

if __name__ == "__main__":
    main()