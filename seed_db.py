from app import app
from extensions import db
from models import Student, Report
from ml_model import train_and_save_model, predict_risk
import random

def seed_database():
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        
        # Check if we already have data
        if Student.query.count() > 0:
            print("Database already seeded.")
            return

        print("Training ML model and generating initial predictions...")
        train_and_save_model()

        print("Seeding students...")
        # Create some dummy students
        students_data = [
            {"name": "Alice Johnson", "gpa": 3.8, "attendance": 95, "assignments": 48},
            {"name": "Bob Smith", "gpa": 2.1, "attendance": 65, "assignments": 20},
            {"name": "Charlie Davis", "gpa": 3.2, "attendance": 88, "assignments": 40},
            {"name": "Diana Prince", "gpa": 1.5, "attendance": 45, "assignments": 10},
            {"name": "Evan Wright", "gpa": 2.8, "attendance": 78, "assignments": 35},
        ]

        for s_data in students_data:
            risk_score, risk_label = predict_risk(s_data["gpa"], s_data["attendance"], s_data["assignments"])
            student = Student(
                name=s_data["name"],
                gpa=s_data["gpa"],
                attendance=s_data["attendance"],
                assignments_completed=s_data["assignments"],
                risk_score=risk_score,
                risk_label=risk_label
            )
            db.session.add(student)
        
        db.session.commit()

        print("Seeding reports...")
        # Add some pending reports
        students = Student.query.all()
        for i in range(2):
            report = Report(student_id=random.choice(students).id, status="Pending")
            db.session.add(report)
            
        db.session.commit()
        print("Database seeded successfully!")

if __name__ == "__main__":
    seed_database()
