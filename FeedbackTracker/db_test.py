import os
import sys
import logging
from app import app, db
from models import User, ROLE_CC, ROLE_HOD, ROLE_PRINCIPAL

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_database():
    logger.info("Starting database test")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Current directory: {os.getcwd()}")
    
    # Check database configuration
    db_uri = app.config.get("SQLALCHEMY_DATABASE_URI")
    logger.info(f"Database URI: {db_uri}")
    
    with app.app_context():
        try:
            # Clear existing users (optional, for testing only)
            logger.info("Clearing existing users...")
            User.query.delete()
            db.session.commit()
            
            # Create a test user
            logger.info("Creating test user...")
            test_user = User(
                username="testuser",
                email="test@example.com", 
                role=ROLE_CC,
                department="Test Department"
            )
            test_user.set_password("test123")
            db.session.add(test_user)
            db.session.commit()
            
            # Create staff users with specific credentials
            logger.info("Creating staff users...")
            
            # CC
            cc_user = User(
                username="cc_user",
                email="cc@college.com",
                role=ROLE_CC,
                department="Computer Science"
            )
            cc_user.set_password("cc123")
            db.session.add(cc_user)
            db.session.commit()
            
            # HOD
            hod_user = User(
                username="hod_user",
                email="hod@college.com",
                role=ROLE_HOD,
                department="Computer Science"
            )
            hod_user.set_password("hod123")
            db.session.add(hod_user)
            db.session.commit()
            
            # Principal
            principal_user = User(
                username="principal_user",
                email="principal@college.com",
                role=ROLE_PRINCIPAL
            )
            principal_user.set_password("principal123")
            db.session.add(principal_user)
            db.session.commit()
            
            # Verify all users were created
            all_users = User.query.all()
            logger.info(f"Created {len(all_users)} users:")
            for user in all_users:
                logger.info(f"  - {user.username} ({user.email}), role: {user.role}")
                
            # Test reading back a user and checking password
            test_user = User.query.filter_by(email="cc@college.com").first()
            if test_user:
                logger.info(f"Found user: {test_user.username}")
                if test_user.check_password("cc123"):
                    logger.info("Password check succeeded")
                else:
                    logger.error("Password check failed")
            else:
                logger.error("User not found")
                
            logger.info("Database test completed successfully")
            
        except Exception as e:
            logger.error(f"Error during database test: {e}")
            db.session.rollback()

if __name__ == "__main__":
    test_database()