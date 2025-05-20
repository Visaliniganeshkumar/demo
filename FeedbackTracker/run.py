from app import app, db  # noqa: F401
import routes  # noqa: F401
import logging
import os
import sys
import shutil
from routes import initialize_database

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print("Starting feedback management system")
print("Python version:", sys.version)

# Reset the database
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'feedback_system.db')
if os.path.exists(db_path):
    print(f"Removing existing database at {db_path}")
    os.remove(db_path)

# Initialize the database with demo data
with app.app_context():
    try:
        # Create tables
        db.create_all()
        print("Database tables created successfully")
        
        # Initialize with demo data
        initialize_database()
        print("\nDatabase initialized successfully with:")
        print("- CC user (cc@college.com / cc123)")
        print("- HOD user (hod@college.com / hod123)")
        print("- Principal user (principal@college.com / principal123)")
        
        # Verify users exist
        from models import User
        users = User.query.all()
        print(f"\nFound {len(users)} users in the database")
        for user in users:
            print(f"- {user.username} ({user.email}, role: {user.role})")
    except Exception as e:
        print(f"Error initializing database: {e}")

print("\nServer ready to start on http://0.0.0.0:5000")
print("Open your browser to access the application")
print("Debug route available at: http://0.0.0.0:5000/debug/users")

# Start the server
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)