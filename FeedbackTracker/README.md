# Feedback Management System

A comprehensive feedback management system for educational institutions, featuring role-based access, sentiment analysis, and feedback tracking.

## Quick Start

To run the application manually (using Flask's development server):

```bash
python runapp.py
```

The application will be available at: http://0.0.0.0:5000 or through your Replit URL.

## Default Login Credentials

The following staff accounts are automatically created in the system:

- **CC (Class Coordinator)**
  - Email: cc@college.com
  - Password: cc123

- **HOD (Head of Department)**
  - Email: hod@college.com
  - Password: hod123

- **Principal**
  - Email: principal@college.com
  - Password: principal123

## System Verification

To verify the system is running correctly, visit:

```
/check
```

This will display a system status page showing database connectivity and available user accounts.

## Troubleshooting

If you encounter any issues with the application failing to start through the Replit workflow, you can run it manually using the instructions above.

## Features

- Role-based access (Student, CC, HOD, Principal)
- Star-based rating system for feedback
- Sentiment analysis of text feedback
- Category-based feedback collection
- Feedback tracking and response
- Anonymous feedback option
- Dashboard analytics

## Technical Overview

- Backend: Python Flask
- Database: SQLite
- Text Analysis: BERT-based sentiment analysis
- Frontend: Bootstrap with custom components