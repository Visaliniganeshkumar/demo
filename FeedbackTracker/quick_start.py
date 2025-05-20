import logging
import sys
from app import app, db
from models import User, ROLE_CC, ROLE_HOD, ROLE_PRINCIPAL

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Verify staff accounts are in the database
def verify_accounts():
    with app.app_context():
        try:
            # Check if staff accounts exist
            cc_user = User.query.filter_by(email="cc@college.com").first()
            hod_user = User.query.filter_by(email="hod@college.com").first()
            principal_user = User.query.filter_by(email="principal@college.com").first()
            
            logger.info("Account verification results:")
            logger.info(f"  CC User: {'EXISTS' if cc_user else 'MISSING'}")
            logger.info(f"  HOD User: {'EXISTS' if hod_user else 'MISSING'}")
            logger.info(f"  Principal User: {'EXISTS' if principal_user else 'MISSING'}")
            
            # If any are missing, we should create them
            if not (cc_user and hod_user and principal_user):
                logger.info("Creating missing staff accounts...")
                
                # Create CC user if missing
                if not cc_user:
                    cc_user = User()
                    cc_user.username = "cc_user"
                    cc_user.email = "cc@college.com"
                    cc_user.role = ROLE_CC
                    cc_user.department = "Computer Science"
                    cc_user.set_password("cc123")
                    db.session.add(cc_user)
                    db.session.commit()
                    logger.info("Created CC user")
                
                # Create HOD user if missing
                if not hod_user:
                    hod_user = User()
                    hod_user.username = "hod_user"
                    hod_user.email = "hod@college.com"
                    hod_user.role = ROLE_HOD
                    hod_user.department = "Computer Science"
                    hod_user.set_password("hod123")
                    db.session.add(hod_user)
                    db.session.commit()
                    logger.info("Created HOD user")
                
                # Create Principal user if missing
                if not principal_user:
                    principal_user = User()
                    principal_user.username = "principal_user"
                    principal_user.email = "principal@college.com"
                    principal_user.role = ROLE_PRINCIPAL
                    principal_user.set_password("principal123")
                    db.session.add(principal_user)
                    db.session.commit()
                    logger.info("Created Principal user")
        except Exception as e:
            logger.error(f"Error verifying accounts: {e}")

# Start the server - with account verification
if __name__ == "__main__":
    logger.info(f"Python version: {sys.version}")
    logger.info("Starting account verification...")
    verify_accounts()
    logger.info("Starting Flask application...")
    app.run(host="0.0.0.0", port=5000)