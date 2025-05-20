import logging
import traceback
import sys
from flask import request

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

try:
    from app import app
    
    # Add error handling
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal server error: {error}")
        logger.error(traceback.format_exc())
        return "Internal Server Error", 500
    
    @app.before_request
    def log_request_info():
        logger.debug('Headers: %s', request.headers)
        logger.debug('Body: %s', request.get_data())
        
    @app.after_request
    def log_response_info(response):
        logger.debug('Response status: %s', response.status)
        logger.debug('Response headers: %s', response.headers)
        return response
        
    if __name__ == '__main__':
        logger.info("Starting app with debug logging")
        app.run(host='0.0.0.0', port=5000, debug=True)
        
except Exception as e:
    logger.critical(f"Critical error initializing app: {e}")
    logger.critical(traceback.format_exc())
    sys.exit(1)