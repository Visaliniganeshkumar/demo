"""
Script to check the database structure
"""
import os
import sqlite3
import json

# Database path
db_path = os.path.join(os.getcwd(), 'feedback_system.db')

def check_table_structure(table_name):
    """Check the structure of a table"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get table info
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    
    # Format the output
    column_info = []
    for col in columns:
        column_info.append({
            "cid": col[0],
            "name": col[1],
            "type": col[2],
            "notnull": col[3],
            "default_value": col[4],
            "pk": col[5]
        })
    
    conn.close()
    return column_info

if __name__ == "__main__":
    # Check DirectMessage table
    print("DirectMessage table structure:")
    columns = check_table_structure("direct_message")
    print(json.dumps(columns, indent=2))