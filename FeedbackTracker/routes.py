import logging
import json
from datetime import datetime, timedelta
from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from sqlalchemy import func, desc, and_, or_, distinct

from app import app, db
from models import (
    User, Category, Question, Feedback, FeedbackItem, Rating, Response, DirectMessage,
    ROLE_STUDENT, ROLE_CC, ROLE_HOD, ROLE_PRINCIPAL,
    STATUS_PENDING, STATUS_ACCEPTED, STATUS_FORWARDED, STATUS_RESOLVED, STATUS_UPLOADED,
    STATUS_REVIEWED, STATUS_NOTED
)
from bert_analysis import analyze_text, aspect_based_analysis

logger = logging.getLogger(__name__)

# Initialize the database with default categories and questions
# For Flask 2.0+, we need to use with app.app_context() instead of before_first_request
def initialize_database():
    # This function will be called manually in main.py
    logger.info("Starting database initialization")
    try:
        # Create required users (regardless of whether the database is initialized)
        # These users need to exist for the system to work

        # Create test admin user first
        try:
            # First, delete any existing direct messages with NULL sender_id
            DirectMessage.query.filter(DirectMessage.sender_id.is_(None)).delete()
            db.session.commit()
            logger.info("Cleared problematic direct messages")

            # Delete existing admin user if exists
            admin = User.query.filter_by(email="admin@example.com").first()
            if admin:
                db.session.delete(admin)
                db.session.commit()
                logger.info("Deleted existing admin user")

            # Create new admin user
            admin = User()
            admin.username = "admin"
            admin.email = "admin@example.com"
            admin.role = ROLE_PRINCIPAL
            admin.set_password("admin123")
            db.session.add(admin)
            db.session.commit()
            logger.info(f"Admin user created with ID: {admin.id}")

            # 2. Create CC user
            cc = User.query.filter_by(email="cc@college.com").first()
            if cc:
                db.session.delete(cc)
                db.session.commit()
                logger.info("Deleted existing CC user")

            cc_user = User()
            cc_user.username = "cc_user"
            cc_user.email = "cc@college.com"
            cc_user.role = ROLE_CC
            cc_user.department = "Computer Science"
            cc_user.set_password("cc123")
            db.session.add(cc_user)
            db.session.commit()
            logger.info(f"CC user created with ID: {cc_user.id}")

            # 3. Create HOD user
            hod = User.query.filter_by(email="hod@college.com").first()
            if hod:
                db.session.delete(hod)
                db.session.commit()
                logger.info("Deleted existing HOD user")

            hod_user = User()
            hod_user.username = "hod_user"
            hod_user.email = "hod@college.com"
            hod_user.role = ROLE_HOD
            hod_user.department = "Computer Science"
            hod_user.set_password("hod123")
            db.session.add(hod_user)
            db.session.commit()
            logger.info(f"HOD user created with ID: {hod_user.id}")

            # 4. Create Principal user
            principal = User.query.filter_by(email="principal@college.com").first()
            if principal:
                db.session.delete(principal)
                db.session.commit()
                logger.info("Deleted existing Principal user")

            principal_user = User()
            principal_user.username = "principal_user"
            principal_user.email = "principal@college.com"
            principal_user.role = ROLE_PRINCIPAL
            principal_user.set_password("principal123")
            db.session.add(principal_user)
            db.session.commit()
            logger.info(f"Principal user created with ID: {principal_user.id}")

            # Check all created users
            all_users = User.query.all()
            logger.info(f"Total users in database: {len(all_users)}")
            for user in all_users:
                logger.info(f"User in DB: {user.username} ({user.email}), role: {user.role}")

        except Exception as e:
            logger.error(f"Error creating users: {e}")
            db.session.rollback()
            raise

        # Check if categories already exist
        if Category.query.first() is None:
            # Create default categories
            categories = [
                {"name": "Teaching Quality", "description": "Evaluate the quality of teaching and instruction"},
                {"name": "Course Content", "description": "Evaluate the course material and curriculum"},
                {"name": "Infrastructure", "description": "Feedback on college infrastructure and facilities"},
                {"name": "Laboratory Facilities", "description": "Evaluate the lab equipment and resources"},
                {"name": "Administration", "description": "Feedback on administrative processes"},
                {"name": "Library Resources", "description": "Evaluate library facilities and resources"},
                {"name": "Extracurricular Activities", "description": "Feedback on college events and activities"},
                {"name": "Other", "description": "Any other feedback not covered by the categories above"}
            ]

            for cat_data in categories:
                category = Category()
                category.name = cat_data["name"]
                category.description = cat_data["description"]
                db.session.add(category)

            db.session.commit()

            # Add default questions for each category
            questions = {
                "Teaching Quality": [
                    "How would you rate the clarity of lectures?",
                    "How effectively does the teacher engage students?",
                    "How accessible are the teachers for doubts and questions?",
                    "How well does the teacher relate theory to practical applications?"
                ],
                "Course Content": [
                    "How relevant is the course content to your career goals?",
                    "How up-to-date is the course material?",
                    "How well-structured is the curriculum?",
                    "How helpful are the assignments and projects?"
                ],
                "Infrastructure": [
                    "How would you rate the classroom facilities?",
                    "How satisfied are you with the Wi-Fi and internet facilities?",
                    "How well-maintained are the common areas?",
                    "How comfortable are the seating arrangements?"
                ],
                "Laboratory Facilities": [
                    "How adequate is the lab equipment for practical learning?",
                    "How well-maintained are the lab facilities?",
                    "How helpful are the lab assistants?",
                    "How accessible are the labs outside of regular hours?"
                ],
                "Administration": [
                    "How efficiently does the administration handle student requests?",
                    "How transparent are the administrative processes?",
                    "How helpful is the administrative staff?",
                    "How well are student grievances addressed?"
                ],
                "Library Resources": [
                    "How well-stocked is the library with relevant resources?",
                    "How helpful is the library staff?",
                    "How accessible are digital resources?",
                    "How comfortable is the library environment for studying?"
                ],
                "Extracurricular Activities": [
                    "How diverse are the extracurricular opportunities?",
                    "How well-organized are college events?",
                    "How encouraging is the college towards student participation?",
                    "How beneficial are these activities to your overall development?"
                ]
            }

            for cat_name, question_list in questions.items():
                category = Category.query.filter_by(name=cat_name).first()
                if category:
                    for q_text in question_list:
                        question = Question()
                        question.category_id = category.id
                        question.text = q_text
                        db.session.add(question)

            db.session.commit()
            logger.info("Database initialized with default categories and questions")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        db.session.rollback()


@app.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.is_student():
            return redirect(url_for('dashboard_student'))
        else:
            return redirect(url_for('dashboard_staff'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Debug information
        logger.info(f"Login attempt - Email: {email}")

        user = User.query.filter_by(email=email).first()

        if user is None:
            logger.warning(f"Login failed - User not found for email: {email}")
            flash('Invalid email or password', 'danger')
            return redirect(url_for('login'))

        # More debug info
        logger.info(f"User found - ID: {user.id}, Role: {user.role}")

        if not user.check_password(password):
            logger.warning(f"Login failed - Invalid password for user: {email}")
            flash('Invalid email or password', 'danger')
            return redirect(url_for('login'))

        login_user(user, remember=True)
        next_page = request.args.get('next')

        if not next_page or not next_page.startswith('/'):
            if user.is_student():
                next_page = url_for('dashboard_student')
            else:
                next_page = url_for('dashboard_staff')

        return redirect(next_page)

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        email = request.form.get('email')

        user = User.query.filter_by(email=email).first()

        if user:
            # In a real application, send a password reset email
            # For this demo, we'll just reset the password directly
            new_password = "temporarypassword123"  # In real app, generate a random password
            user.set_password(new_password)
            db.session.commit()

            flash('Password has been reset. Please check your email.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Email not found in our records.', 'danger')

    return render_template('reset_password.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    # Only staff can register new users, redirect to login
    return redirect(url_for('login'))


@app.route('/dashboard/student')
@login_required
def dashboard_student():
    if not current_user.is_student():
        flash('Access denied. Students only.', 'danger')
        return redirect(url_for('index'))

    # Get recent feedback submissions
    recent_feedback = Feedback.query.filter_by(student_id=current_user.id).order_by(Feedback.submission_date.desc()).limit(5).all()

    # Get feedback with pending responses
    pending_feedback = (Feedback.query
                       .join(Response, Feedback.id == Response.feedback_id)
                       .filter(Feedback.student_id == current_user.id)
                       .filter(Response.status == STATUS_PENDING)
                       .all())

    # Get recent responses to feedback
    recent_responses = (Response.query
                       .join(Feedback, Feedback.id == Response.feedback_id)
                       .filter(Feedback.student_id == current_user.id)
                       .order_by(Response.response_date.desc())
                       .limit(5)
                       .all())

    return render_template('dashboard_student.html', 
                          recent_feedback=recent_feedback,
                          pending_feedback=pending_feedback,
                          recent_responses=recent_responses,
                          Response=Response)


@app.route('/dashboard/staff')
@login_required
def dashboard_staff():
    if not current_user.is_staff():
        flash('Access denied. Staff only.', 'danger')
        return redirect(url_for('index'))

    # Date range for filtering (default: last 30 days)
    days = request.args.get('days', 30, type=int)
    from_date = datetime.utcnow() - timedelta(days=days)

    # Get total feedback count
    total_feedback = Feedback.query.filter(Feedback.submission_date >= from_date).count()

    # Get pending feedback count
    pending_count = (Response.query
                    .filter(Response.status == STATUS_PENDING)
                    .filter(Response.response_date >= from_date)
                    .count())

    # Get category-wise feedback counts
    category_counts = (db.session.query(
                        Category.name, 
                        func.count(FeedbackItem.id))
                      .join(FeedbackItem, Category.id == FeedbackItem.category_id)
                      .join(Feedback, FeedbackItem.feedback_id == Feedback.id)
                      .filter(Feedback.submission_date >= from_date)
                      .group_by(Category.name)
                      .all())

    # Get today's feedback
    today = datetime.utcnow().date()
    today_feedback = (Feedback.query
                     .filter(func.date(Feedback.submission_date) == today)
                     .order_by(Feedback.submission_date.desc())
                     .all())

    # Get recent feedback with low ratings (average rating <= 2)
    low_ratings = (db.session.query(Feedback)
                  .join(FeedbackItem, Feedback.id == FeedbackItem.feedback_id)
                  .join(Rating, FeedbackItem.id == Rating.feedback_item_id)
                  .group_by(Feedback.id)
                  .having(func.avg(Rating.rating_value) <= 2)
                  .filter(Feedback.submission_date >= from_date)
                  .order_by(Feedback.submission_date.desc())
                  .limit(5)
                  .all())

    # Get feedback requiring attention (pending responses)
    attention_needed = (Feedback.query
                       .join(Response, Feedback.id == Response.feedback_id)
                       .filter(Response.status == STATUS_PENDING)
                       .filter(Response.staff_id == current_user.id)
                       .order_by(Feedback.submission_date.desc())
                       .all())

    # For visualization: Average ratings by category
    avg_ratings = (db.session.query(
                   Category.name, 
                   func.avg(Rating.rating_value).label('avg_rating'))
                  .join(FeedbackItem, Category.id == FeedbackItem.category_id)
                  .join(Rating, FeedbackItem.id == Rating.feedback_item_id)
                  .join(Feedback, FeedbackItem.feedback_id == Feedback.id)
                  .filter(Feedback.submission_date >= from_date)
                  .group_by(Category.name)
                  .all())

    # Sentiment analysis summary
    sentiment_summary = (db.session.query(
                        FeedbackItem.sentiment_label,
                        func.count(FeedbackItem.id))
                       .filter(FeedbackItem.sentiment_label.isnot(None))
                       .join(Feedback, FeedbackItem.feedback_id == Feedback.id)
                       .filter(Feedback.submission_date >= from_date)
                       .group_by(FeedbackItem.sentiment_label)
                       .all())

    # Get direct messages for the message center
    received_messages = DirectMessage.query.filter_by(recipient_id=current_user.id).order_by(DirectMessage.sent_date.desc()).limit(10).all()
    sent_messages = DirectMessage.query.filter_by(sender_id=current_user.id).order_by(DirectMessage.sent_date.desc()).limit(10).all()
    unread_messages = DirectMessage.query.filter_by(recipient_id=current_user.id, is_read=False).count()

    # Get potential recipients for messaging (initialize with empty list as default)
    recipients = []

    if current_user.is_cc():
        # CC can message students in their department, HOD, and principal
        recipients = User.query.filter(
            or_(
                and_(User.role == ROLE_STUDENT, User.department == current_user.department),
                and_(User.role == ROLE_HOD, User.department == current_user.department),
                User.role == ROLE_PRINCIPAL
            )
        ).all()
    elif current_user.is_hod():
        # HOD can message students, CCs in their department, and principal
        recipients = User.query.filter(
            or_(
                and_(User.role.in_([ROLE_STUDENT, ROLE_CC]), User.department == current_user.department),
                User.role == ROLE_PRINCIPAL
            )
        ).all()
    elif current_user.is_principal():
        # Principal can message all users
        recipients = User.query.filter(User.id != current_user.id).all()

    # Get staff members for forwarding feedback
    staff_members = User.query.filter(
        User.role.in_([ROLE_CC, ROLE_HOD, ROLE_PRINCIPAL]),
        User.id != current_user.id
    ).all()

    return render_template('dashboard_staff.html',
                          total_feedback=total_feedback,
                          pending_count=pending_count,
                          category_counts=category_counts,
                          today_feedback=today_feedback,
                          low_ratings=low_ratings,
                          attention_needed=attention_needed,
                          avg_ratings=avg_ratings,
                          sentiment_summary=sentiment_summary,
                          days=days,
                          received_messages=received_messages,
                          unread_messages=unread_messages,
                          recipients=recipients,
                          staff_members=staff_members,
                          Response=Response)


@app.route('/feedback/submit', methods=['GET', 'POST'])
@login_required
def submit_feedback():
    if not current_user.is_student():
        flash('Access denied. Students only.', 'danger')
        return redirect(url_for('index'))

    if request.method == 'POST':
        try:
            # Create new feedback entry
            is_anonymous = 'anonymous' in request.form
            feedback = Feedback()
            feedback.student_id = current_user.id
            feedback.is_anonymous = is_anonymous
            db.session.add(feedback)
            db.session.flush()  # Get feedback ID without committing

            # Check if submitting specific category
            submit_category = request.form.get('submit_category')

            if submit_category:
                # Handle single category submission
                selected_categories = [Category.query.get_or_404(submit_category)]
            else:
                # Handle multiple categories
                selected_category_ids = request.form.getlist('selected_categories')
                selected_categories = []
                if selected_category_ids:
                    selected_categories = Category.query.filter(Category.id.in_(selected_category_ids)).all()

            # Always include "Other" category if it has text
            other_category = Category.query.filter_by(name="Other").first()
            if other_category and other_category not in selected_categories:
                other_text = request.form.get(f'text_{other_category.id}', '').strip()
                if other_text:
                    selected_categories.append(other_category)

            # Ensure at least one category or text feedback in "Other"
            if not selected_categories:
                raise ValueError("No categories selected and no feedback provided")

            # Process each selected category's feedback
            for category in selected_categories:
                text_feedback = request.form.get(f'text_{category.id}', '').strip()

                # For "Other" category, only process if text is provided
                if category.name == "Other" and not text_feedback:
                    continue

                # Create feedback item for this category
                feedback_item = FeedbackItem()
                feedback_item.feedback_id = feedback.id
                feedback_item.category_id = category.id
                feedback_item.text_feedback = text_feedback
                db.session.add(feedback_item)
                db.session.flush()  # Get feedback item ID

                # Skip ratings for "Other" category as it only has text
                if category.name != "Other":
                    # Process ratings for this category
                    total_rating = 0
                    rating_count = 0

                    for question in category.questions:
                        rating_value = int(request.form.get(f'rating_{question.id}', 0))
                        if rating_value > 0:  # Only save valid ratings (1-5)
                            rating = Rating()
                            rating.feedback_item_id = feedback_item.id
                            rating.question_id = question.id
                            rating.rating_value = rating_value
                            db.session.add(rating)

                            # Add to totals for sentiment calculation
                            total_rating += rating_value
                            rating_count += 1

                    # Calculate average rating for sentiment if we have ratings
                    # Note: We're not requiring ratings for every question, just using what's provided
                    if rating_count > 0:
                        avg_rating = total_rating / rating_count

                        # Assign sentiment based on average rating
                        # 1-1.8: Very Negative, 1.8-2.6: Negative, 2.6-3.4: Neutral, 3.4-4.2: Positive, 4.2-5: Very Positive
                        if avg_rating < 1.8:
                            sentiment_score = 0.1
                            sentiment_label = "Very Negative"
                        elif avg_rating < 2.6:
                            sentiment_score = 0.3
                            sentiment_label = "Negative"
                        elif avg_rating < 3.4:
                            sentiment_score = 0.5
                            sentiment_label = "Neutral"
                        elif avg_rating < 4.2:
                            sentiment_score = 0.7
                            sentiment_label = "Positive"
                        else:
                            sentiment_score = 0.9
                            sentiment_label = "Very Positive"

                        # Only override sentiment if text analysis didn't already set it
                        if not feedback_item.sentiment_score:
                            feedback_item.sentiment_score = sentiment_score
                            feedback_item.sentiment_label = sentiment_label

                # Run BERT analysis on text feedback if provided
                text_sentiment_score = None
                text_sentiment_label = None
                if text_feedback:
                    text_sentiment_score, text_sentiment_label = analyze_text(text_feedback)
                    aspects = aspect_based_analysis(text_feedback)
                    feedback_item.aspect_based_results = json.dumps(aspects)

                # Determine final sentiment by combining ratings and text feedback
                if text_sentiment_score is not None and feedback_item.sentiment_score is not None:
                    # If we have both rating and text sentiment, use a weighted average (60% text, 40% rating)
                    combined_score = (text_sentiment_score * 0.6) + (feedback_item.sentiment_score * 0.4)

                    # Determine label from combined score
                    if combined_score < 0.2:
                        combined_label = "very negative"
                    elif combined_score < 0.4:
                        combined_label = "negative" 
                    elif combined_score < 0.6:
                        combined_label = "neutral"
                    elif combined_score < 0.8:
                        combined_label = "positive"
                    else:
                        combined_label = "very positive"

                    feedback_item.sentiment_score = combined_score
                    feedback_item.sentiment_label = combined_label

                elif text_sentiment_score is not None:
                    # Only text sentiment available
                    feedback_item.sentiment_score = text_sentiment_score
                    feedback_item.sentiment_label = text_sentiment_label

                # If no sentiment is set yet (only ratings, no text), the rating-based sentiment from above will remain

            # Create initial response record (pending status)
            # Assign to CC by default
            cc_staff = User.query.filter_by(role=ROLE_CC, department=current_user.department).first()
            if cc_staff:
                response = Response()
                response.feedback_id = feedback.id
                response.staff_id = cc_staff.id
                response.response_text = "Feedback received and pending review."
                response.status = STATUS_PENDING
                db.session.add(response)

            db.session.commit()
            flash('Your feedback has been submitted successfully!', 'success')
            return redirect(url_for('dashboard_student'))

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error submitting feedback: {e}")
            flash('An error occurred while submitting your feedback.', 'danger')

    # GET method - display feedback form
    categories = Category.query.all()

    return render_template('feedback_form.html', categories=categories)


@app.route('/feedback/track')
@login_required
def track_feedback():
    if not current_user.is_student():
        flash('Access denied. Students only.', 'danger')
        return redirect(url_for('index'))

    # Get all feedback by the student
    feedbacks = (Feedback.query
                .filter_by(student_id=current_user.id)
                .order_by(Feedback.submission_date.desc())
                .all())

    return render_template('feedback_tracking.html', feedbacks=feedbacks)


@app.route('/feedback/view/<int:feedback_id>')
@login_required
def view_feedback(feedback_id):
    feedback = Feedback.query.get_or_404(feedback_id)

    # Check permissions
    if current_user.is_student() and feedback.student_id != current_user.id:
        flash('Access denied. You can only view your own feedback.', 'danger')
        return redirect(url_for('index'))

    # Staff can view feedback based on role hierarchy and assignments
    if current_user.is_staff():
        has_access = False

        # CC can view feedback from students in their department
        if current_user.is_cc() and feedback.student.department == current_user.department:
            has_access = True

        # HOD can view feedback forwarded to them or replied to by them
        elif current_user.is_hod():
            for response in feedback.responses:
                # HOD can view if feedback was forwarded to them or they responded to it
                if response.forwarded_to == current_user.id or response.staff_id == current_user.id:
                    has_access = True
                    break

        # Principal can view feedback forwarded to them or replied to by them
        elif current_user.is_principal():
            for response in feedback.responses:
                # Principal can view if feedback was forwarded to them or they responded to it
                if response.forwarded_to == current_user.id or response.staff_id == current_user.id:
                    has_access = True
                    break

        if not has_access:
            flash('Access denied. You are not assigned to this feedback.', 'danger')
            return redirect(url_for('dashboard_staff'))

    # Get feedback items and responses
    feedback_items = FeedbackItem.query.filter_by(feedback_id=feedback.id).all()

    # Filter responses based on role permissions
    if current_user.is_student():
        # Students see all responses to their feedback
        responses = Response.query.filter_by(feedback_id=feedback.id).order_by(Response.response_date).all()
    elif current_user.is_cc():
        # CC sees all responses for this feedback
        responses = Response.query.filter_by(feedback_id=feedback.id).order_by(Response.response_date).all()
    elif current_user.is_hod():
        # HOD sees all CC responses, any responses forwarded to them, and their own responses
        # Also sees principal responses if the feedback was forwarded by HOD to principal
        hod_visible_responses = []
        all_responses = Response.query.filter_by(feedback_id=feedback.id).order_by(Response.response_date).all()

        # Track if HOD forwarded to Principal
        hod_forwarded_to_principal = False
        for r in all_responses:
            if r.staff_id == current_user.id and r.forwarded_to:
                forwarded_user = User.query.get(r.forwarded_to)
                if forwarded_user and forwarded_user.is_principal():
                    hod_forwarded_to_principal = True
                    break

        for response in all_responses:
            # HOD can see CC responses and their own
            if response.staff.is_cc() or response.staff_id == current_user.id or response.forwarded_to == current_user.id:
                hod_visible_responses.append(response)
            # HOD can see Principal responses if HOD forwarded to Principal
            elif response.staff.is_principal() and hod_forwarded_to_principal:
                hod_visible_responses.append(response)

        responses = hod_visible_responses
    elif current_user.is_principal():
        # Principal sees responses from HOD or CC forwarded to them, plus their own responses
        # Also sees the response chain that led to them being involved
        principal_visible_responses = []
        all_responses = Response.query.filter_by(feedback_id=feedback.id).order_by(Response.response_date).all()

        # Check if any response is forwarded to principal
        forwarded_to_principal = False
        for r in all_responses:
            if r.forwarded_to == current_user.id:
                forwarded_to_principal = True
                break

        for response in all_responses:
            # Principal can see their own responses
            if response.staff_id == current_user.id:
                principal_visible_responses.append(response)
            # Principal can see responses forwarded to them
            elif response.forwarded_to == current_user.id:
                principal_visible_responses.append(response)
            # If principal is involved, show all responses in the chain
            elif forwarded_to_principal:
                principal_visible_responses.append(response)

        responses = principal_visible_responses
    else:
        responses = []

    # Format responses to show forwarding chain
    response_threads = {}
    for response in responses:
        if not hasattr(response, 'parent_response_id') or response.parent_response_id is None:
            # This is a top-level response
            if response.id not in response_threads:
                response_threads[response.id] = {
                    'response': response,
                    'replies': []
                }
        else:
            # This is a reply to another response
            parent_id = response.parent_response_id
            if parent_id not in response_threads:
                # Create parent entry if it doesn't exist
                response_threads[parent_id] = {
                    'response': None,
                    'replies': []
                }
            response_threads[parent_id]['replies'].append(response)

    # Sort responses by date (newest first)
    sorted_threads = sorted(
        response_threads.values(),
        key=lambda x: x['response'].response_date if x['response'] else datetime.now(),
        reverse=True
    )

    return render_template('feedback_view.html', 
                          feedback=feedback,
                          feedback_items=feedback_items,
                          responses=responses,
                          response_threads=sorted_threads,
                          Response=Response)


@app.route('/respond/<int:feedback_id>', methods=['POST'])
@login_required
def respond_to_feedback(feedback_id):
    if not current_user.is_staff():
        flash('Access denied. Staff only.', 'danger')
        return redirect(url_for('index'))

    feedback = Feedback.query.get_or_404(feedback_id)
    response_text = request.form.get('response', '').strip()
    action = request.form.get('action', 'reply')
    forward_to = request.form.get('forward_to', None)
    parent_response_id = request.form.get('parent_response_id', None)
    forwarded_message = request.form.get('forwarded_message', '')

    if not response_text:
        flash('Response text is required.', 'danger')
        return redirect(url_for('view_feedback', feedback_id=feedback_id))

    try:
        # If this is a reply to a specific message, include reference to that message
        if forwarded_message and forwarded_message.strip():
            response_text = f"[Forwarded Message: {forwarded_message.strip()}]\n\n{response_text}"

        # Create response
        response = Response()
        response.feedback_id = feedback_id
        response.staff_id = current_user.id
        response.response_text = response_text

        # Set parent response if replying to a specific response
        if parent_response_id and parent_response_id.strip():
            try:
                response.parent_response_id = int(parent_response_id)
            except (ValueError, TypeError):
                # If invalid, just ignore the parent reference
                pass

        if action == 'reply':
            status = STATUS_ACCEPTED
            response.status = status

        elif action == 'forward' and forward_to:
            status = STATUS_FORWARDED
            recipient_id = int(forward_to)

            response.status = status
            response.forwarded_to = recipient_id

            # Get forwarded message content if available
            forwarded_message = request.form.get('forwarded_message', '')

            # Add forwarding details
            forward_recipient = User.query.get(recipient_id)
            if forward_recipient:
                # Add message forwarding information for e-commerce style tracking
                forwarder_info = f"Forwarded by {current_user.username} ({current_user.role.upper()}) to {forward_recipient.username} ({forward_recipient.role.upper()})"

                # If there's a forwarded message, include it in a quoted block
                if forwarded_message and forwarded_message.strip():
                    response.response_text = f"{response.response_text}\n\n--- FORWARDED MESSAGE ---\n{forwarded_message}\n\n--- FORWARDING NOTE ---\n{forwarder_info}"
                else:
                    response.response_text = f"{response.response_text}\n\n---\n{forwarder_info}"

        elif action == 'upload' and current_user.is_cc():
            status = STATUS_UPLOADED
            response.status = status

        elif action == 'reviewed' and current_user.is_cc():
            status = STATUS_REVIEWED
            response.status = status

        elif action == 'noted' and current_user.is_hod():
            status = STATUS_NOTED
            response.status = status

        db.session.add(response)
        db.session.commit()
        flash('Your response has been submitted.', 'success')

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error responding to feedback: {e}")
        flash('An error occurred while submitting your response.', 'danger')

    return redirect(url_for('view_feedback', feedback_id=feedback_id))


@app.route('/manage/students', methods=['GET', 'POST'])
@login_required
def manage_students():
    if not current_user.is_cc():
        flash('Access denied. Class coordinators only.', 'danger')
        return redirect(url_for('index'))

    if request.method == 'POST':
        # Add new student
        username = request.form.get('username')
        email = request.form.get('email')
        roll_number = request.form.get('roll_number')
        password = request.form.get('password')
        dob_str = request.form.get('dob')
        dob = None
        if dob_str and dob_str.strip():
            try:
                dob = datetime.strptime(dob_str, '%Y-%m-%d').date()
            except ValueError:
                flash('Invalid date format. Please use YYYY-MM-DD.', 'danger')
                return redirect(url_for('manage_students'))
        address = request.form.get('address')
        department = request.form.get('department')

        # Check if user already exists
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return redirect(url_for('manage_students'))

        if User.query.filter_by(username=username).first():
            flash('Username already taken.', 'danger')
            return redirect(url_for('manage_students'))

        if User.query.filter_by(roll_number=roll_number).first():
            flash('Roll number already registered.', 'danger')
            return redirect(url_for('manage_students'))

        # Create new student
        student = User()
        student.username = username
        student.email = email
        student.role = ROLE_STUDENT
        student.roll_number = roll_number
        student.dob = dob
        student.address = address
        student.department = department
        student.set_password(password)

        db.session.add(student)
        db.session.commit()

        flash('Student added successfully.', 'success')
        return redirect(url_for('manage_students'))

    # Get all students in the CC's department
    students = User.query.filter_by(role=ROLE_STUDENT, department=current_user.department).all()

    return render_template('manage_students.html', students=students)


@app.route('/direct_message', methods=['GET', 'POST'])
@login_required
def direct_message():
    if request.method == 'POST':
        recipient_id = request.form.get('recipient_id', type=int)
        message = request.form.get('message', '').strip()
        original_message_id = request.form.get('original_message_id', type=int)

        if not recipient_id or not message:
            flash('Recipient and message are required.', 'danger')
            return redirect(url_for('direct_message'))

        recipient = User.query.get(recipient_id)
        if not recipient:
            flash('Recipient not found.', 'danger')
            return redirect(url_for('direct_message'))

        # Students can only message staff
        if current_user.is_student() and recipient.is_student():
            flash('Students can only send messages to staff.', 'danger')
            return redirect(url_for('direct_message'))

        # Check if this is a forwarded message
        original_message = None
        if original_message_id:
            original_message = DirectMessage.query.get(original_message_id)
            if original_message:
                # If forwarding, include original message content
                formatted_message = f"{message}\n\n--- Forwarded Message ---\n"
                formatted_message += f"From: {original_message.sender.username}\n"
                formatted_message += f"Date: {original_message.sent_date.strftime('%Y-%m-%d %H:%M')}\n\n"
                formatted_message += original_message.message
                message = formatted_message

        # Create direct message
        dm = DirectMessage()
        dm.sender_id = current_user.id
        dm.recipient_id = recipient_id
        dm.message = message

        # Store parent message reference for forwarded messages
        if original_message:
            dm.parent_message_id = original_message_id

        db.session.add(dm)
        db.session.commit()

        flash('Message sent successfully.', 'success')

        # If request is AJAX, return JSON response
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': True, 'message': 'Message sent successfully'})

        return redirect(url_for('direct_message'))

    # GET request - show inbox/sent messages
    received_messages = DirectMessage.query.filter_by(recipient_id=current_user.id).order_by(DirectMessage.sent_date.desc()).all()
    sent_messages = DirectMessage.query.filter_by(sender_id=current_user.id).order_by(DirectMessage.sent_date.desc()).all()

    # Get potential recipients based on role
    if current_user.is_student():
        # Students can message staff in their department and principal
        recipients = User.query.filter(
            or_(
                and_(User.role.in_([ROLE_CC, ROLE_HOD]), User.department == current_user.department),
                User.role == ROLE_PRINCIPAL  # Direct access to principal regardless of department
            )
        ).all()
    else:
        # Staff can message students in their department and other staff
        recipients = User.query.filter(
            or_(
                and_(User.role == ROLE_STUDENT, User.department == current_user.department),
                and_(User.role.in_([ROLE_CC, ROLE_HOD, ROLE_PRINCIPAL]), User.id != current_user.id)
            )
        ).all()

    return render_template('direct_messages.html',
                          received_messages=received_messages,
                          sent_messages=sent_messages,
                          recipients=recipients)


@app.route('/api/mark_message_read/<int:message_id>', methods=['POST'])
@login_required
def mark_message_read(message_id):
    message = DirectMessage.query.get_or_404(message_id)

    # Ensure user can mark this message as read
    if message.recipient_id != current_user.id:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403

    try:
        message.is_read = True
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/feedback/analytics')
@login_required
def feedback_analytics():
    if not current_user.is_staff():
        return jsonify({'error': 'Unauthorized'}), 403

    # Date range filter options
    days = request.args.get('days', 30, type=int)
    from_date_str = request.args.get('from_date')
    to_date_str = request.args.get('to_date')
    category_filter = request.args.get('category')

    # Set filters based on provided parameters
    if from_date_str and to_date_str:
        try:
            from_date = datetime.strptime(from_date_str, '%Y-%m-%d')
            to_date = datetime.strptime(to_date_str, '%Y-%m-%d') + timedelta(days=1)  # Include end date
        except ValueError:
            # Default to last 30 days if date format is invalid
            from_date = datetime.utcnow() - timedelta(days=days)
            to_date = datetime.utcnow()
    else:
        from_date = datetime.utcnow() - timedelta(days=days)
        to_date = datetime.utcnow()

    # Build base queries with date filters
    feedback_base_query = Feedback.query.filter(
        Feedback.submission_date >= from_date,
        Feedback.submission_date <= to_date
    )

    feedback_item_base_query = FeedbackItem.query.join(
        Feedback, FeedbackItem.feedback_id == Feedback.id
    ).filter(
        Feedback.submission_date >= from_date,
        Feedback.submission_date <= to_date
    )

    # Apply category filter if provided
    if category_filter:
        feedback_item_base_query = feedback_item_base_query.join(
            Category, FeedbackItem.category_id == Category.id
        ).filter(Category.name == category_filter)

    # Get all categories for filter UI
    all_categories = Category.query.all()
    category_list = [{'id': cat.id, 'name': cat.name} for cat in all_categories]

    # Category-wise average ratings with question subcategories
    category_ratings = []
    question_ratings = []

    # Get main category ratings
    category_avg_query = (db.session.query(
                        Category.id,
                        Category.name, 
                        func.avg(Rating.rating_value).label('avg_rating'),
                        func.count(distinct(Rating.id)).label('rating_count'))
                      .join(FeedbackItem, Category.id == FeedbackItem.category_id)
                      .join(Rating, FeedbackItem.id == Rating.feedback_item_id)
                      .join(Feedback, FeedbackItem.feedback_id == Feedback.id)
                      .filter(Feedback.submission_date >= from_date,
                             Feedback.submission_date <= to_date)
                      .group_by(Category.id, Category.name))

    # Apply category filter if provided
    if category_filter:
        category_avg_query = category_avg_query.filter(Category.name == category_filter)

    category_ratings = category_avg_query.all()

    # Get question level ratings (subcategories)
    question_avg_query = (db.session.query(
                        Category.id.label('category_id'),
                        Category.name.label('category_name'),
                        Question.id.label('question_id'),
                        Question.text.label('question_text'),
                        func.avg(Rating.rating_value).label('avg_rating'),
                        func.count(distinct(Rating.id)).label('rating_count'))
                      .join(Question, Category.id == Question.category_id)
                      .join(FeedbackItem, Category.id == FeedbackItem.category_id)
                      .join(Rating, and_(FeedbackItem.id == Rating.feedback_item_id, 
                                      Question.id == Rating.question_id))
                      .join(Feedback, FeedbackItem.feedback_id == Feedback.id)
                      .filter(Feedback.submission_date >= from_date,
                             Feedback.submission_date <= to_date)
                      .group_by(Category.id, Category.name, 
                               Question.id, Question.text))

    # Apply category filter if provided
    if category_filter:
        question_avg_query = question_avg_query.filter(Category.name == category_filter)

    question_ratings = question_avg_query.all()

    # Format data for chart with main categories and subcategories
    chart_data = []
    category_data = {}

    # Process main categories
    for cat_id, cat_name, avg_rating, count in category_ratings:
        if count > 0:  # Only include categories with ratings
            category_data[cat_id] = {
                'name': cat_name,
                'avg_rating': float(avg_rating),
                'questions': []
            }
            chart_data.append({
                'id': f'cat_{cat_id}',
                'label': cat_name,
                'value': float(avg_rating),
                'count': count,
                'isCategory': True
            })

    # Process subcategories (questions)
    for cat_id, cat_name, q_id, q_text, avg_rating, count in question_ratings:
        if cat_id in category_data and count > 0:  # Only include questions with ratings
            # Truncate long question text
            short_q_text = q_text if len(q_text) <= 30 else f"{q_text[:27]}..."

            category_data[cat_id]['questions'].append({
                'id': q_id,
                'text': q_text,
                'short_text': short_q_text,
                'avg_rating': float(avg_rating),
                'count': count
            })

            chart_data.append({
                'id': f'q_{q_id}',
                'label': f"  - {short_q_text}",
                'value': float(avg_rating),
                'count': count,
                'isCategory': False,
                'parentId': f'cat_{cat_id}'
            })

    # Sentiment distribution
    sentiment_counts_query = (db.session.query(
                            FeedbackItem.sentiment_label,
                            func.count(FeedbackItem.id))
                          .filter(FeedbackItem.sentiment_label.isnot(None))
                          .join(Feedback, FeedbackItem.feedback_id == Feedback.id)
                          .filter(Feedback.submission_date >= from_date,
                                 Feedback.submission_date <= to_date))

    # Apply category filter if provided
    if category_filter:
        sentiment_counts_query = sentiment_counts_query.join(
            Category, FeedbackItem.category_id == Category.id
        ).filter(Category.name == category_filter)

    sentiment_counts = sentiment_counts_query.group_by(FeedbackItem.sentiment_label).all()

    # Feedback counts over time (grouped by week)
    feedback_trend_query = (db.session.query(
                          func.strftime('%Y-%W', Feedback.submission_date).label('week'),
                          func.count(Feedback.id))
                         .filter(Feedback.submission_date >= from_date,
                                Feedback.submission_date <= to_date))

    # Apply category filter if provided                         
    if category_filter:
        feedback_ids_with_category = db.session.query(FeedbackItem.feedback_id).join(
            Category, FeedbackItem.category_id == Category.id
        ).filter(Category.name == category_filter).subquery()

        feedback_trend_query = feedback_trend_query.filter(
            Feedback.id.in_(feedback_ids_with_category)
        )

    feedback_trend = feedback_trend_query.group_by('week').order_by('week').all()

    return jsonify({
        'filters': {
            'from_date': from_date.strftime('%Y-%m-%d'),
            'to_date': (to_date - timedelta(days=1)).strftime('%Y-%m-%d'),
            'category': category_filter,
            'available_categories': category_list
        },
        'chart_data': chart_data,
        'category_data': {cat_id: data for cat_id, data in category_data.items()},
        'sentiment_counts': {item[0]: item[1] for item in sentiment_counts if item[0]},
        'feedback_trend': {item[0]: item[1] for item in feedback_trend}
    })


@app.route('/debug/users')
def debug_users():
    """Debugging route to check users in the database"""
    users = User.query.all()
    debug_info = []

    for user in users:
        debug_info.append({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'has_password': bool(user.password_hash)
        })

    # Add test credentials
    test_users = [
        {'email': 'cc@college.com', 'password': 'cc123'},
        {'email': 'hod@college.com', 'password': 'hod123'},
        {'email': 'principal@college.com', 'password': 'principal123'}
    ]

    # Verify test credentials
    verification = []
    for test_user in test_users:
        user = User.query.filter_by(email=test_user['email']).first()
        if user:
            can_login = user.check_password(test_user['password'])
            verification.append({
                'email': test_user['email'],
                'exists': True,
                'password_works': can_login
            })
        else:
            verification.append({
                'email': test_user['email'],
                'exists': False,
                'password_works': False
            })

    return jsonify({
        'user_count': len(users),
        'users': debug_info,
        'verification': verification
    })

@app.route('/api/areas_of_improvement')
@login_required
def api_areas_of_improvement():
    """Get areas of improvement based on feedback with negative sentiment"""
    if not current_user.is_cc():
        return jsonify({'error': 'Access denied'}), 403

    # Get negative feedback items from the department
    negative_items = (FeedbackItem.query
                     .join(Feedback, FeedbackItem.feedback_id == Feedback.id)
                     .join(User, Feedback.student_id == User.id)
                     .join(Category, FeedbackItem.category_id == Category.id)
                     .filter(User.department == current_user.department)
                     .filter(or_(
                         FeedbackItem.sentiment_label == 'very negative',
                         FeedbackItem.sentiment_label == 'negative'
                     ))
                     .order_by(FeedbackItem.sentiment_score)
                     .limit(10)
                     .all())

    # Group feedback by category
    improvement_areas = {}
    for item in negative_items:
        category = item.category.name
        if category not in improvement_areas:
            improvement_areas[category] = {
                'count': 0,
                'comments': [],
                'avg_sentiment': 0.0
            }

        improvement_areas[category]['count'] += 1
        if item.text_feedback:
            improvement_areas[category]['comments'].append(item.text_feedback)
        improvement_areas[category]['avg_sentiment'] += float(item.sentiment_score or 0)

    # Calculate average sentiment
    for category in improvement_areas:
        if improvement_areas[category]['count'] > 0:
            improvement_areas[category]['avg_sentiment'] /= improvement_areas[category]['count']

    # Sort by count (most feedback first)
    sorted_areas = [
        {
            'category': category,
            'count': data['count'],
            'comments': data['comments'][:3],  # Limit to 3 comments per category
            'avg_sentiment': round(data['avg_sentiment'], 2)
        }
        for category, data in sorted(
            improvement_areas.items(),
            key=lambda x: x[1]['count'],
            reverse=True
        )
    ]

    return jsonify({'areas': sorted_areas})


@app.route('/download_report')
@login_required
def download_report():
    if not current_user.is_staff():
        flash('Access denied. Staff only.', 'danger')
        return redirect(url_for('index'))

    import csv
    from io import StringIO
    from flask import Response as FlaskResponse

    # Create CSV file in memory
    si = StringIO()
    csv_writer = csv.writer(si)

    # Add header row
    csv_writer.writerow(['Feedback ID', 'Date', 'Student', 'Department', 'Category', 'Avg. Rating', 'Sentiment', 'Comments', 'Improvement Needed'])

    # Get all feedback relevant to this staff member
    if current_user.is_cc():
        # For CC, get all feedback from their department
        feedbacks = (Feedback.query
                   .join(User, Feedback.student_id == User.id)
                   .filter(User.department == current_user.department)
                   .order_by(Feedback.submission_date.desc())
                   .all())
    elif current_user.is_hod() or current_user.is_principal():
        # For HOD/Principal, get feedback that was forwarded to them
        feedbacks = (Feedback.query
                    .join(Response, Feedback.id == Response.feedback_id)
                    .filter(Response.forwarded_to == current_user.id)
                    .order_by(Feedback.submission_date.desc())
                    .all())
    else:
        # Default empty list if no match (shouldn't normally happen)
        feedbacks = []

    # Populate data rows
    for feedback in feedbacks:
        student_name = "Anonymous" if feedback.is_anonymous else feedback.student.username
        student_dept = feedback.student.department

        for item in feedback.items:
            category_name = item.category.name

            # Calculate average rating for this category
            ratings = Rating.query.filter_by(feedback_item_id=item.id).all()
            avg_rating = sum(r.rating_value for r in ratings) / len(ratings) if ratings else 'N/A'
            if isinstance(avg_rating, (int, float)):
                avg_rating = f"{avg_rating:.2f}"

            sentiment = item.sentiment_label.capitalize() if item.sentiment_label else 'N/A'
            comments = item.text_feedback if item.text_feedback else 'No comments'

            # Determine if this needs improvement (based on sentiment or low rating)
            needs_improvement = False
            improvement_note = ""

            if item.sentiment_label in ['negative', 'very negative']:
                needs_improvement = True
                improvement_note = "Needs attention - Negative sentiment detected"
            elif avg_rating != 'N/A' and float(avg_rating) < 2.7:
                needs_improvement = True
                improvement_note = f"Needs attention - Low rating ({avg_rating}/5)"

            csv_writer.writerow([
                feedback.id,
                feedback.submission_date.strftime('%Y-%m-%d'),
                student_name,
                student_dept,
                category_name,
                avg_rating,
                sentiment,
                comments,
                improvement_note
            ])

    # Create response
    output = si.getvalue()
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    response = FlaskResponse(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment;filename=feedback_report_{timestamp}.csv"}
    )

    return response


@app.route('/areas_of_improvement')
@login_required
def areas_of_improvement():
    if not current_user.is_cc():
        flash('Access denied. CC only.', 'danger')
        return redirect(url_for('index'))

    # Determine date range (last 30 days by default)
    days = request.args.get('days', 30, type=int)
    from_date = datetime.now() - timedelta(days=days)

    # Get categories with lowest average ratings
    low_rated_categories = (db.session.query(
                           Category.name,
                           func.avg(Rating.rating_value).label('avg_rating'))
                          .join(FeedbackItem, Category.id == FeedbackItem.category_id)
                          .join(Rating, FeedbackItem.id == Rating.feedback_item_id)
                          .join(Feedback, FeedbackItem.feedback_id == Feedback.id)
                          .join(User, Feedback.student_id == User.id)
                          .filter(Feedback.submission_date >= from_date)
                          .filter(User.department == current_user.department)
                          .group_by(Category.name)
                          .order_by(func.avg(Rating.rating_value).asc())
                          .limit(3)
                          .all())

    # Get aspects with most negative sentiment
    negative_aspects = []
    feedback_items = (FeedbackItem.query
                     .join(Feedback, FeedbackItem.feedback_id == Feedback.id)
                     .join(User, Feedback.student_id == User.id)
                     .filter(User.department == current_user.department)
                     .filter(Feedback.submission_date >= from_date)
                     .filter(FeedbackItem.sentiment_label == 'negative')
                     .filter(FeedbackItem.aspect_based_results.isnot(None))
                     .all())

    aspect_counts = {}
    for item in feedback_items:
        if item.aspect_based_results:
            try:
                aspects = json.loads(item.aspect_based_results)
                for aspect, data in aspects.items():
                    if data.get('sentiment') == 'negative':
                        aspect_counts[aspect] = aspect_counts.get(aspect, 0) + 1
            except:
                pass

    # Sort aspects by count
    negative_aspects = sorted(aspect_counts.items(), key=lambda x: x[1], reverse=True)[:5]

    return jsonify({
        'low_rated_categories': [{
            'name': cat[0], 
            'avg_rating': float(cat[1])
        } for cat in low_rated_categories],
        'negative_aspects': [{
            'aspect': aspect.replace('_', ' ').title(), 
            'count': count
        } for aspect, count in negative_aspects]
    })


@app.route('/sentiment_trends')
@login_required
def sentiment_trends():
    """Endpoint to get sentiment trends over time for visualization"""
    if not current_user.is_staff():
        flash('Access denied. Staff only.', 'danger')
        return redirect(url_for('index'))

    # Get parameters
    period = request.args.get('period', 'month')  # month, quarter, year
    days = request.args.get('days', 365, type=int)  # Default to 1 year of data
    department = request.args.get('department', None)  # Optional department filter

    # Determine date range
    from_date = datetime.now() - timedelta(days=days)

    # Base query - filter by date
    query = (db.session.query(
            func.date_trunc(period, Feedback.submission_date).label('period'),
            FeedbackItem.sentiment_label,
            func.count(FeedbackItem.id).label('count')
        )
        .join(Feedback, FeedbackItem.feedback_id == Feedback.id)
        .filter(Feedback.submission_date >= from_date)
    )

    # Apply department filter for CC users
    if current_user.is_cc() or department:
        dept = department or current_user.department
        query = query.join(User, Feedback.student_id == User.id).filter(User.department == dept)

    # Group by period and sentiment
    results = (query
        .group_by(func.date_trunc(period, Feedback.submission_date), FeedbackItem.sentiment_label)
        .order_by(func.date_trunc(period, Feedback.submission_date))
        .all()
    )

    # Format results for visualization
    trends = {}
    for period_date, sentiment, count in results:
        period_str = period_date.strftime('%Y-%m')
        if period_str not in trends:
            trends[period_str] = {'positive': 0, 'neutral': 0, 'negative': 0}

        if sentiment in trends[period_str]:
            trends[period_str][sentiment] = count

    # Fill in missing periods
    all_periods = []
    current_date = from_date
    end_date = datetime.now()

    if period == 'month':
        while current_date <= end_date:
            period_str = current_date.strftime('%Y-%m')
            all_periods.append(period_str)
            # Add one month
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1)

    # Ensure all periods exist in trends
    for period_str in all_periods:
        if period_str not in trends:
            trends[period_str] = {'positive': 0, 'neutral': 0, 'negative': 0}

    # Calculate sentiment ratio for each period
    sentiment_ratio = {}
    for period_str, counts in trends.items():
        total = sum(counts.values())
        if total > 0:
            sentiment_ratio[period_str] = {
                'positive_ratio': round(counts['positive'] / total * 100, 1),
                'neutral_ratio': round(counts['neutral'] / total * 100, 1),
                'negative_ratio': round(counts['negative'] / total * 100, 1),
                'total': total
            }
        else:
            sentiment_ratio[period_str] = {
                'positive_ratio': 0,
                'neutral_ratio': 0,
                'negative_ratio': 0,
                'total': 0
            }

    # Return results
    return jsonify({
        'trend_data': sorted([(p, d) for p, d in trends.items()], key=lambda x: x[0]),
        'sentiment_ratio': sorted([(p, d) for p, d in sentiment_ratio.items()], key=lambda x: x[0]),
        'period': period,
        'days': days
    })


@app.route('/ai_feedback_suggestions')
@login_required
def ai_feedback_suggestions():
    """Get AI-powered suggestions for improving areas with negative feedback"""
    if not current_user.is_staff():
        flash('Access denied. Staff only.', 'danger')
        return redirect(url_for('index'))

    # Get parameters
    days = request.args.get('days', 90, type=int)  # Default to last 90 days
    category_id = request.args.get('category_id', None, type=int)

    # Determine date range
    from_date = datetime.now() - timedelta(days=days)

    # Base query - filter by date and negative sentiment
    query = (db.session.query(FeedbackItem)
        .join(Feedback, FeedbackItem.feedback_id == Feedback.id)
        .filter(Feedback.submission_date >= from_date)
        .filter(FeedbackItem.sentiment_label == 'negative')
        .filter(FeedbackItem.text_feedback.isnot(None))
    )

    # Apply department filter for CC users
    if current_user.is_cc():
        query = query.join(User, Feedback.student_id == User.id).filter(User.department == current_user.department)

    # Apply category filter if provided
    if category_id:
        query = query.filter(FeedbackItem.category_id == category_id)

    # Get negative feedback items
    feedback_items = query.all()

    # Collect text feedback for analysis
    all_feedback = " ".join([item.text_feedback for item in feedback_items if item.text_feedback])

    # Generate suggestions based on common themes in feedback
    suggestions = []

    if all_feedback:
        # Extract common themes and issues
        # This would use more sophisticated AI in a production system
        # For now, we'll use a simplified approach based on keyword matching

        # Define keywords for common issues and corresponding suggestions
        improvement_areas = {
            'difficult': {
                'theme': 'Complexity',
                'suggestion': 'Consider simplifying complex topics and providing more scaffolded learning materials.'
            },
            'confusing': {
                'theme': 'Clarity',
                'suggestion': 'Review explanations for clarity and provide more visual aids or examples.'
            },
            'slow': {
                'theme': 'Pacing',
                'suggestion': 'Evaluate the pacing of instruction and consider offering additional resources for self-paced learning.'
            },
            'boring': {
                'theme': 'Engagement',
                'suggestion': 'Incorporate more interactive activities and real-world applications to increase engagement to increase engagement.'
            },
            'outdated': {
                'theme': 'Relevance',
                'suggestion': 'Update materials with current industry practices and technologies.'
            },
            'hard': {
                'theme': 'Difficulty',
                'suggestion': 'Consider providing additional practice opportunities and more graduated difficulty levels.'
            },
            'too much': {
                'theme': 'Workload',
                'suggestion': 'Review the workload and consider adjusting assignment deadlines or requirements.'
            }
        }

        # Check for keywords in feedback
        for keyword, data in improvement_areas.items():
            if keyword in all_feedback.lower():
                # Count occurrences to prioritize suggestions
                count = all_feedback.lower().count(keyword)
                suggestions.append({
                    'theme': data['theme'],
                    'suggestion': data['suggestion'],
                    'relevance': count
                })

        # Sort by relevance (occurrence count)
        suggestions = sorted(suggestions, key=lambda x: x['relevance'], reverse=True)

    # If no specific suggestions, provide general ones
    if not suggestions:
        suggestions = [
            {
                'theme': 'General Improvement',
                'suggestion': 'Consider collecting more detailed feedback through targeted surveys or focus groups.',
                'relevance': 1
            },
            {
                'theme': 'Communication',
                'suggestion': 'Enhance communication channels to proactively address student concerns.',
                'relevance': 1
            }
        ]

    return jsonify({
        'suggestions': suggestions,
        'feedback_count': len(feedback_items),
        'days': days
    })


@app.route('/generate_pdf_report')
@login_required
def generate_pdf_report():
    """Generate a comprehensive PDF report with visualization and analysis"""
    from flask import Response as FlaskResponse
    from report_generator import create_feedback_report

    if not current_user.is_staff():
        flash('Access denied. Staff only.', 'danger')
        return redirect(url_for('index'))

    # Get parameters
    days = request.args.get('days', 365, type=int)
    department = request.args.get('department', None)
    report_type = request.args.get('type', 'full')  # full, sentiment, categories

    # Determine date range
    from_date = datetime.now() - timedelta(days=days)

    # Base query filters
    department_filter = None
    if current_user.is_cc() or department:
        dept = department or current_user.department
        department_filter = User.department == dept

    # Get total feedback count
    query = Feedback.query.filter(Feedback.submission_date >= from_date)
    if department_filter is not None:
        query = query.join(User, Feedback.student_id == User.id).filter(department_filter)
    total_feedback = query.count()

    # Get sentiment summary
    query = (db.session.query(
            FeedbackItem.sentiment_label,
            func.count(FeedbackItem.id).label('count')
        )
        .join(Feedback, FeedbackItem.feedback_id == Feedback.id)
        .filter(Feedback.submission_date >= from_date)
    )

    if department_filter is not None:
        query = query.join(User, Feedback.student_id == User.id).filter(department_filter)

    sentiment_counts = {label: 0 for label in ['positive', 'neutral', 'negative']}
    results = query.group_by(FeedbackItem.sentiment_label).all()

    total_with_sentiment = 0
    for label, count in results:
        if label in sentiment_counts:
            sentiment_counts[label] = count
            total_with_sentiment += count

    sentiment_summary = {}
    if total_with_sentiment > 0:
        for label, count in sentiment_counts.items():
            sentiment_summary[label] = round(count / total_with_sentiment * 100, 1)

    # Get sentiment trends data
    sentiment_trends_data = []
    sentiment_ratio_data = []
    if 'full' in report_type or 'sentiment' in report_type:
        # Get trend data from sentiment_trends endpoint
        resp = sentiment_trends()
        if isinstance(resp, str):
            try:
                trend_data = json.loads(resp)
                sentiment_trends_data = trend_data.get('trend_data', [])
                sentiment_ratio_data = trend_data.get('sentiment_ratio', [])
            except (json.JSONDecodeError, TypeError):
                pass  # Handle JSON parsing issues

    # Get category ratings
    category_ratings = {}
    category_details = {}

    query = (db.session.query(
            Category.name,
            func.avg(Rating.rating_value).label('avg_rating'),
            func.count(Rating.id).label('count')
        )
        .join(FeedbackItem, Category.id == FeedbackItem.category_id)
        .join(Rating, FeedbackItem.id == Rating.feedback_item_id)
        .join(Feedback, FeedbackItem.feedback_id == Feedback.id)
        .filter(Feedback.submission_date >= from_date)
    )

    if department_filter is not None:
        query = query.join(User, Feedback.student_id == User.id).filter(department_filter)

    results = query.group_by(Category.name).all()

    for category_name, avg_rating, count in results:
        category_ratings[category_name] = float(avg_rating)
        category_details[category_name] = {
            'avg_rating': float(avg_rating),
            'count': count,
            'positive_percent': 0,
            'negative_percent': 0
        }

    # Get sentiment breakdown by category
    query = (db.session.query(
            Category.name,
            FeedbackItem.sentiment_label,
            func.count(FeedbackItem.id).label('count')
        )
        .join(Category, FeedbackItem.category_id == Category.id)
        .join(Feedback, FeedbackItem.feedback_id == Feedback.id)
        .filter(Feedback.submission_date >= from_date)
        .filter(FeedbackItem.sentiment_label.isnot(None))
    )

    if department_filter is not None:
        query = query.join(User, Feedback.student_id == User.id).filter(department_filter)

    results = query.group_by(Category.name, FeedbackItem.sentiment_label).all()

    for category_name, sentiment, count in results:
        if category_name in category_details:
            total = category_details[category_name]['count']
            if sentiment == 'positive':
                category_details[category_name]['positive_percent'] = round(count / total * 100, 1)
            elif sentiment == 'negative':
                category_details[category_name]['negative_percent'] = round(count / total * 100, 1)

    # Get improvement suggestions
    improvement_suggestions = []
    if 'full' in report_type:
        # Get suggestions from AI endpoint
        resp = ai_feedback_suggestions()
        if hasattr(resp, 'json'):
            try:
                suggestions_data = resp.json
                if suggestions_data is not None and isinstance(suggestions_data, dict):
                    improvement_suggestions = suggestions_data.get('suggestions', [])
            except:
                # Handle any issues with json parsing
                improvement_suggestions = []

    # Get areas for improvement
    low_rated_categories = []
    if 'full' in report_type or 'categories' in report_type:
        # Get lowest rated categories
        sorted_categories = sorted(category_ratings.items(), key=lambda x: x[1])
        low_rated_categories = [
            {
                'theme': cat_name,
                'description': f"Average rating: {rating:.2f}/5.0. Consider focusing improvement efforts in this area."
            }
            for cat_name, rating in sorted_categories[:3] if rating < 3.5
        ]

    # Prepare report data
    report_data = {
        'department': department or (current_user.department if current_user.is_cc() else 'All Departments'),
        'days': days,
        'total_feedback': total_feedback,
        'num_categories': len(category_ratings),
        'sentiment_summary': sentiment_summary,
        'category_ratings': category_ratings,
        'category_details': category_details,
        'improvement_suggestions': improvement_suggestions,
        'areas_for_improvement': low_rated_categories,
        'conclusion': "This report highlights key trends and areas for improvement based on student feedback analysis. "
                    "Regular monitoring and targeted improvements can lead to enhanced educational outcomes."
    }

    # Add trend data if available
    if sentiment_trends_data:
        report_data['sentiment_trends'] = sentiment_trends_data
        report_data['sentiment_ratio'] = sentiment_ratio_data

    # Generate the PDF
    pdf_bytes = create_feedback_report(report_data)

    # Create response
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    response = FlaskResponse(
        pdf_bytes,
        mimetype='application/pdf',
        headers={'Content-Disposition': f'attachment; filename=feedback_report_{timestamp}.pdf'}
    )

    return response


@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', error_code=404, error_message="Page not found"), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('error.html', error_code=500, error_message="Internal server error"), 500
@app.route('/api/check_new_messages')
@login_required
def check_new_messages():
    unread_count = DirectMessage.query.filter_by(
        recipient_id=current_user.id,
        is_read=False
    ).count()

    return jsonify({'new_messages': unread_count})
@app.route('/manage/courses', methods=['GET', 'POST'])
@login_required
def manage_courses():
    if not current_user.is_cc():
        flash('Access denied. Class coordinators only.', 'danger')
        return redirect(url_for('index'))

    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add':
            course_name = request.form.get('name')
            staff_id = request.form.get('staff_id')
            category_id = request.form.get('category_id')

            course = Course(name=course_name, staff_id=staff_id, category_id=category_id)
            db.session.add(course)
            db.session.commit()
            flash('Course added successfully.', 'success')

        elif action == 'delete':
            course_id = request.form.get('course_id')
            course = Course.query.get_or_404(course_id)
            db.session.delete(course)
            db.session.commit()
            flash('Course deleted successfully.', 'success')

    courses = Course.query.all()
    staff = Staff.query.all()
    categories = Category.query.all()
    return render_template('manage_courses.html', courses=courses, staff=staff, categories=categories)

@app.route('/manage/staff', methods=['GET', 'POST'])
@login_required
def manage_staff():
    if not current_user.is_cc():
        flash('Access denied. Class coordinators only.', 'danger')
        return redirect(url_for('index'))

    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add':
            staff_name = request.form.get('name')
            department = request.form.get('department')

            staff = Staff(name=staff_name, department=department)
            db.session.add(staff)
            db.session.commit()
            flash('Staff added successfully.', 'success')

        elif action == 'delete':
            staff_id = request.form.get('staff_id')
            staff = Staff.query.get_or_404(staff_id)
            db.session.delete(staff)
            db.session.commit()
            flash('Staff deleted successfully.', 'success')

    staff_members = Staff.query.all()
    return render_template('manage_staff.html', staff_members=staff_members)

@app.route('/category_analysis/<int:category_id>')
@login_required
def category_analysis(category_id):
    if not current_user.is_cc():
        flash('Access denied. Class coordinators only.', 'danger')
        return redirect(url_for('index'))

    category = Category.query.get_or_404(category_id)

    # Get feedback analysis for the category
    feedback_items = FeedbackItem.query.filter_by(category_id=category_id).all()

    # Analyze ratings
    avg_ratings = db.session.query(
        Question.text,
        func.avg(Rating.rating_value)
    ).join(Rating).filter(
        Rating.feedback_item_id.in_([item.id for item in feedback_items])
    ).group_by(Question.text).all()

    # Analyze text feedback
    text_feedback = [item.text_feedback for item in feedback_items if item.text_feedback]
    sentiment_counts = Counter([item.sentiment_label for item in feedback_items if item.sentiment_label])

    return render_template(
        'category_analysis.html',
        category=category,
        avg_ratings=avg_ratings,
        text_feedback=text_feedback,
        sentiment_counts=sentiment_counts
    )