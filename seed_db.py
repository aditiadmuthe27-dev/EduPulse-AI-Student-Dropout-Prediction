from app import app
from extensions import db, bcrypt
from models import User, Student, Report
from ml_model import predict_risk
import random
import os

def seed_database():
    with app.app_context():
        print("Dropping existing tables...")
        db.drop_all()
        print("Creating database tables...")
        db.create_all()
        
        print("Creating admin user...")
        hashed_pw = bcrypt.generate_password_hash("admin123").decode('utf-8')
        admin = User(username="admin", email="admin@edupulse.com", password_hash=hashed_pw, role="Admin")
        db.session.add(admin)

        print("Seeding students...")
        students_data = [
            {"name": "Alice Johnson", "gpa": 3.8, "attendance": 95, "assignments": 48},
            {"name": "Bob Smith", "gpa": 2.1, "attendance": 65, "assignments": 20},
            {"name": "Charlie Davis", "gpa": 3.2, "attendance": 88, "assignments": 40},
            {"name": "Diana Prince", "gpa": 1.5, "attendance": 45, "assignments": 10},
            {"name": "Evan Wright", "gpa": 2.8, "attendance": 78, "assignments": 35},
        ]

        for s_data in students_data:
            risk_label, confidence = predict_risk(s_data["gpa"], s_data["attendance"], s_data["assignments"])
            student = Student(
                name=s_data["name"],
                gpa=s_data["gpa"],
                attendance=s_data["attendance"],
                assignments_completed=s_data["assignments"],
                risk_score=confidence,
                risk_label=risk_label
            )
            db.session.add(student)
        
        db.session.commit()
        
        print("Creating student users...")
        students = Student.query.all()
        for i, s in enumerate(students):
            hashed_pw = bcrypt.generate_password_hash("student123").decode('utf-8')
            s_user = User(
                username=f"student{i+1}",
                email=f"student{i+1}@example.com",
                password_hash=hashed_pw,
                role="Student",
                student_id=s.id
            )
            db.session.add(s_user)

            # Add some reports
            report = Report(student_id=s.id, status="Generated", confidence_score=s.risk_score)
            db.session.add(report)

        db.session.commit()
        print("Database seeded successfully!")
        print("Admin Login: admin / admin123")
        print("Student Login: student1 / student123")

if __name__ == "__main__":
    seed_database()
