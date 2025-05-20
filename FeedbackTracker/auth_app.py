from flask import Flask, render_template, redirect, url_for, flash, request
from werkzeug.security import check_password_hash
from app import db, app

# Import user model 
from models import User, ROLE_CC, ROLE_HOD, ROLE_PRINCIPAL

# Create a simplified login route
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Try to find the user
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            # Login successful
            return f"""
            <html>
            <head>
                <title>Login Success</title>
                <link href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css" rel="stylesheet">
            </head>
            <body>
                <div class="container mt-5">
                    <div class="alert alert-success">
                        <h4>Login Successful!</h4>
                        <p>Welcome {user.username}. You are logged in as a {user.role}.</p>
                    </div>
                </div>
            </body>
            </html>
            """
        else:
            # Login failed
            return f"""
            <html>
            <head>
                <title>Login Failed</title>
                <link href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css" rel="stylesheet">
            </head>
            <body>
                <div class="container mt-5">
                    <div class="alert alert-danger">
                        <h4>Login Failed</h4>
                        <p>Invalid email or password. Please try again.</p>
                        <p><a href="/" class="btn btn-primary">Try Again</a></p>
                    </div>
                </div>
            </body>
            </html>
            """
    
    # GET request - show login form
    return f"""
    <html>
    <head>
        <title>Feedback System Login</title>
        <link href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css" rel="stylesheet">
    </head>
    <body>
        <div class="container mt-5">
            <div class="row justify-content-center">
                <div class="col-md-6">
                    <div class="card border-0 shadow-sm">
                        <div class="card-header bg-primary text-white">
                            <h4 class="mb-0">Feedback Management System</h4>
                        </div>
                        <div class="card-body">
                            <h5 class="card-title">Login</h5>
                            <form method="POST" action="/">
                                <div class="mb-3">
                                    <label for="email" class="form-label">Email address</label>
                                    <input type="email" class="form-control" id="email" name="email" required>
                                </div>
                                <div class="mb-3">
                                    <label for="password" class="form-label">Password</label>
                                    <input type="password" class="form-control" id="password" name="password" required>
                                </div>
                                <button type="submit" class="btn btn-primary">Login</button>
                            </form>
                            
                            <div class="mt-4">
                                <h6>Test Accounts:</h6>
                                <ul>
                                    <li>CC: cc@college.com / cc123</li>
                                    <li>HOD: hod@college.com / hod123</li>
                                    <li>Principal: principal@college.com / principal123</li>
                                </ul>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

# Run the app
if __name__ == '__main__':
    # First ensure accounts exist
    with app.app_context():
        # Check if we have our staff accounts
        users = User.query.all()
        if len(users) == 0:
            # Create staff accounts
            cc_user = User()
            cc_user.username = "cc_user"
            cc_user.email = "cc@college.com"
            cc_user.role = ROLE_CC
            cc_user.department = "Computer Science"
            cc_user.set_password("cc123")
            db.session.add(cc_user)
            
            hod_user = User()
            hod_user.username = "hod_user"
            hod_user.email = "hod@college.com"
            hod_user.role = ROLE_HOD
            hod_user.department = "Computer Science"
            hod_user.set_password("hod123")
            db.session.add(hod_user)
            
            principal_user = User()
            principal_user.username = "principal_user"
            principal_user.email = "principal@college.com"
            principal_user.role = ROLE_PRINCIPAL
            principal_user.set_password("principal123")
            db.session.add(principal_user)
            
            db.session.commit()
            print("Created staff accounts")
    
    # Run the app
    app.run(host='0.0.0.0', port=5000)