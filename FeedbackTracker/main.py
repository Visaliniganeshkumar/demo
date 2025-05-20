
from app import app, db
import routes  # noqa: F401
import logging
import os
import sys
from routes import initialize_database

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    logger.info("Starting Feedback Management System")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Current directory: {os.getcwd()}")
    logger.info(f"Database URL: {app.config.get('SQLALCHEMY_DATABASE_URI')}")

    # Initialize database with demo data
    with app.app_context():
        try:
            initialize_database()
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            return

    # Run the Flask application
    app.run(host='0.0.0.0', port=5000, debug=True)

if __name__ == "__main__":
    main()
