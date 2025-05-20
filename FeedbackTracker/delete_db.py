
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def delete_database():
    db_path = 'feedback_system.db'
    try:
        if os.path.exists(db_path):
            os.remove(db_path)
            logger.info(f"Successfully deleted {db_path}")
        else:
            logger.info(f"Database {db_path} does not exist")
    except Exception as e:
        logger.error(f"Error deleting database: {e}")

if __name__ == "__main__":
    delete_database()
