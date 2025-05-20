"""
Database migration script to add parent_response_id column to Response table
"""
import os
import logging
import sqlite3
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database path
DB_PATH = "feedback_system.db"

def migrate_database():
    """Add parent_response_id column to Response table"""
    try:
        # Connect to the database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check if column already exists
        cursor.execute("PRAGMA table_info(response)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        if 'parent_response_id' not in column_names:
            logger.info("Adding parent_response_id column to Response table")
            
            # Add the column
            cursor.execute("ALTER TABLE response ADD COLUMN parent_response_id INTEGER")
            
            # Add foreign key constraint (SQLite doesn't support ADD CONSTRAINT in ALTER TABLE)
            # We'll create a new table with the constraint and copy data
            
            # Create backup of existing data
            backup_table = f"response_backup_{int(datetime.now().timestamp())}"
            cursor.execute(f"CREATE TABLE {backup_table} AS SELECT * FROM response")
            logger.info(f"Created backup table: {backup_table}")
            
            # Commit changes
            conn.commit()
            logger.info("Migration completed successfully")
        else:
            logger.info("Column parent_response_id already exists in Response table")
            
    except Exception as e:
        logger.error(f"Error migrating database: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    migrate_database()