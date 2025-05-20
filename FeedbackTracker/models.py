from app import db
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# User roles constants
ROLE_STUDENT = 'student'
ROLE_CC = 'cc'  # Class coordinator
ROLE_HOD = 'hod'  # Head of department
ROLE_PRINCIPAL = 'principal'

# Feedback status constants
STATUS_PENDING = 'pending'
STATUS_ACCEPTED = 'accepted'
STATUS_FORWARDED = 'forwarded'
STATUS_RESOLVED = 'resolved'
STATUS_UPLOADED = 'uploaded'
STATUS_REVIEWED = 'reviewed'
STATUS_NOTED = 'noted'


class User(UserMixin, db.Model):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    date_joined = db.Column(db.DateTime, default=datetime.utcnow)

    # Student specific fields
    roll_number = db.Column(db.String(20), unique=True, nullable=True)
    dob = db.Column(db.Date, nullable=True)
    address = db.Column(db.String(200), nullable=True)
    department = db.Column(db.String(100), nullable=True)

    # Relationship with Feedback
    submitted_feedback = db.relationship('Feedback', backref='student', lazy='dynamic',
                                         foreign_keys='Feedback.student_id')

    # Relationship with Response
    responses = db.relationship('Response', backref='staff', lazy='dynamic',
                                foreign_keys='Response.staff_id')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_student(self):
        return self.role == ROLE_STUDENT

    def is_cc(self):
        return self.role == ROLE_CC

    def is_hod(self):
        return self.role == ROLE_HOD

    def is_principal(self):
        return self.role == ROLE_PRINCIPAL

    def is_staff(self):
        return self.role in [ROLE_CC, ROLE_HOD, ROLE_PRINCIPAL]

    def __repr__(self):
        return f'<User {self.username}>'


class Course(db.Model):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    staff_id = db.Column(db.Integer, db.ForeignKey('staff.id'))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))

class Staff(db.Model):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100))
    courses = db.relationship('Course', backref='staff', lazy='dynamic')

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200))

    # Relationship with Question
    questions = db.relationship('Question', backref='category', lazy='dynamic')

    # Relationship with FeedbackItem
    feedback_items = db.relationship('FeedbackItem', backref='category', lazy='dynamic')

    # Relationship with Courses
    courses = db.relationship('Course', backref='category', lazy='dynamic')

    def __repr__(self):
        return f'<Category {self.name}>'


class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    text = db.Column(db.String(300), nullable=False)

    # Relationship with Rating
    ratings = db.relationship('Rating', backref='question', lazy='dynamic')

    def __repr__(self):
        return f'<Question {self.text[:20]}>'


class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    submission_date = db.Column(db.DateTime, default=datetime.utcnow)
    is_anonymous = db.Column(db.Boolean, default=False)

    # Relationship with FeedbackItem
    items = db.relationship('FeedbackItem', backref='feedback', lazy='dynamic')

    # Relationship with Response
    responses = db.relationship('Response', backref='feedback', lazy='dynamic')

    def __repr__(self):
        # Get student from relationship if not anonymous
        if self.is_anonymous:
            return f'<Feedback #{self.id} by Anonymous>'
        else:
            student = User.query.get(self.student_id)
            if student:
                return f'<Feedback #{self.id} by {student.username}>'
            else:
                return f'<Feedback #{self.id}>'


class FeedbackItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    feedback_id = db.Column(db.Integer, db.ForeignKey('feedback.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    text_feedback = db.Column(db.Text, nullable=True)

    # Relationship with Rating
    ratings = db.relationship('Rating', backref='feedback_item', lazy='dynamic')

    # BERT analysis results
    sentiment_score = db.Column(db.Float, nullable=True)
    sentiment_label = db.Column(db.String(20), nullable=True)
    aspect_based_results = db.Column(db.Text, nullable=True)  # JSON string of aspect-based analysis

    def __repr__(self):
        # Get category from relationship
        category = Category.query.get(self.category_id)
        if category:
            return f'<FeedbackItem #{self.id} for {category.name}>'
        else:
            return f'<FeedbackItem #{self.id}>'


class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    feedback_item_id = db.Column(db.Integer, db.ForeignKey('feedback_item.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    rating_value = db.Column(db.Integer, nullable=False)  # 1 to 5

    def __repr__(self):
        return f'<Rating {self.rating_value} for Q{self.question_id}>'


class Response(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    feedback_id = db.Column(db.Integer, db.ForeignKey('feedback.id'), nullable=False)
    staff_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    response_text = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), nullable=False, default=STATUS_PENDING)
    forwarded_to = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    response_date = db.Column(db.DateTime, default=datetime.utcnow)
    parent_response_id = db.Column(db.Integer, db.ForeignKey('response.id'), nullable=True)

    # Relationship for forwarded_to user
    forwarded_user = db.relationship('User', foreign_keys=[forwarded_to], backref='forwarded_responses')

    # Self-referential relationship for response chain (replies)
    parent_response = db.relationship('Response', remote_side=[id], backref='child_responses', foreign_keys=[parent_response_id])

    def __repr__(self):
        return f'<Response #{self.id} Status: {self.status}>'


class DirectMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    sent_date = db.Column(db.DateTime, default=datetime.utcnow)
    parent_message_id = db.Column(db.Integer, db.ForeignKey('direct_message.id'), nullable=True)

    # Relationships
    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_messages')
    recipient = db.relationship('User', foreign_keys=[recipient_id], backref='received_messages')
    parent_message = db.relationship('DirectMessage', remote_side=[id], backref='forwarded_messages', foreign_keys=[parent_message_id])

    def __repr__(self):
        return f'<DirectMessage #{self.id} from {self.sender.username} to {self.recipient.username}>'