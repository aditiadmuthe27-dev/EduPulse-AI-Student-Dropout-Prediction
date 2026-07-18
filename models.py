from extensions import db
from datetime import datetime
from flask_login import UserMixin

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='Student') # Admin, Student
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=True)
    
    student = db.relationship('Student', backref=db.backref('user', uselist=False))

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    gpa = db.Column(db.Float, nullable=False)
    attendance = db.Column(db.Float, nullable=False)
    assignments_completed = db.Column(db.Integer, nullable=False)
    risk_score = db.Column(db.Float, nullable=True)
    risk_label = db.Column(db.String(20), nullable=True) # e.g., Low, Medium, High

class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    status = db.Column(db.String(50), default='Pending')
    confidence_score = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    student = db.relationship('Student', backref=db.backref('reports', lazy=True))
