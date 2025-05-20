#!/bin/bash

# First, run our database setup script to ensure users exist
python db_test.py

# Then start the Flask app directly (faster than gunicorn for testing)
python quick_start.py