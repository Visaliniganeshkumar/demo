"""
A simplified runner script for the Feedback Management System
"""
import os
import logging
import sys
from app import app
from models import db, User
from flask import render_template

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    logger.info(f"Python version: {sys.version}")
    with app.app_context():
        try:
            admin = User.query.filter_by(username='admin').first()
            if admin:
                logger.info(f"Admin user exists: {admin.username} (ID: {admin.id})")
            else:
                logger.info("No admin user found")
                
            # Print all users
            users = User.query.all()
            logger.info(f"Total users: {len(users)}")
            for user in users:
                logger.info(f"User: {user.username} (ID: {user.id}, Role: {user.role})")
        except Exception as e:
            logger.error(f"Error checking users: {e}")
            
    # Run the application
    logger.info("Starting server...")
    app.run(host='0.0.0.0', port=5000, debug=False)