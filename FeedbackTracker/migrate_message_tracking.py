"""
Database migration script to add parent_message_id column to DirectMessage table
"""
import os
import logging
import sqlite3

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database path
db_path = os.path.join(os.getcwd(), 'feedback_system.db')

def check_column_exists(cursor, table_name, column_name):
    """Check if column exists in the table"""
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    return any(column[1] == column_name for column in columns)

def migrate_direct_messages():
    """Add parent_message_id column to DirectMessage table"""
    try:
        logger.info(f"Connecting to database at {db_path}")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check if column already exists
        if not check_column_exists(cursor, 'direct_message', 'parent_message_id'):
            logger.info("Adding parent_message_id column to DirectMessage table")

            # Create temporary table with correct schema
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS direct_message_temp (
                    id INTEGER PRIMARY KEY,
                    sender_id INTEGER NOT NULL,
                    recipient_id INTEGER NOT NULL,
                    message TEXT NOT NULL,
                    is_read BOOLEAN DEFAULT 0,
                    sent_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    parent_message_id INTEGER,
                    FOREIGN KEY (sender_id) REFERENCES user(id),
                    FOREIGN KEY (recipient_id) REFERENCES user(id),
                    FOREIGN KEY (parent_message_id) REFERENCES direct_message(id)
                )
            ''')

            # Copy existing data with default sender_id
            cursor.execute('''
                INSERT INTO direct_message_temp (id, sender_id, recipient_id, message, is_read, sent_date, parent_message_id)
                SELECT 
                    id,
                    CASE 
                        WHEN sender_id IS NULL THEN (SELECT id FROM user WHERE role = 'cc' LIMIT 1)
                        ELSE sender_id 
                    END,
                    recipient_id,
                    message,
                    is_read,
                    sent_date,
                    parent_message_id
                FROM direct_message
            ''')

            # Drop old table and rename new one
            cursor.execute('DROP TABLE direct_message')
            cursor.execute('ALTER TABLE direct_message_temp RENAME TO direct_message')

            conn.commit()

            logger.info("Migration completed successfully")
        else:
            logger.info("Column parent_message_id already exists")

        conn.close()
        return True

    except Exception as e:
        logger.error(f"Migration failed: {e}")
        if conn:
            conn.close()
        return False

if __name__ == "__main__":
    logger.info("Starting migration for DirectMessage table")
    success = migrate_direct_messages()
    if success:
        logger.info("Migration completed successfully")
    else:
        logger.error("Migration failed")