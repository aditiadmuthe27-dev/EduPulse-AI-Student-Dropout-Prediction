from flask import Flask, render_template, request, redirect, url_for, Response, jsonify, session, g, flash
import os
import csv
import io
from datetime import datetime, timedelta

from extensions import db
from models import Student, Report, User

app = Flask(__name__)
app.secret_key = "edupulse_secure_secret_key_2026"

basedir = os.path.abspath(os.path.dirname(__file__))

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "edupulse.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

@app.before_request
def require_login():
    # Load user if logged in
    user_id = session.get("user_id")
    if user_id:
        g.user = User.query.get(user_id)
    else:
        g.user = None

    # Define exempt endpoints
    if not g.user:
        if request.endpoint not in ["login", "static"]:
            return redirect(url_for("login"))


def get_risk_counts():
    total_students = Student.query.count()
    high_risk_students = Student.query.filter_by(risk_label="High").count()
    medium_risk_students = Student.query.filter_by(risk_label="Medium").count()
    low_risk_students = Student.query.filter_by(risk_label="Low").count()
    return total_students, high_risk_students, medium_risk_students, low_risk_students


def get_trend_data():
    months = []
    low_series, medium_series, high_series = [], [], []
    total, high, medium, low = get_risk_counts()
    today = datetime.utcnow()
    for i in range(5, -1, -1):
        month_date = today - timedelta(days=30 * i)
        months.append(month_date.strftime("%b %Y"))
        low_series.append(max(low - i * 2, 0))
        medium_series.append(max(medium - i, 0))
        high_series.append(max(high - (i // 2), 0))
    return months, low_series, medium_series, high_series


@app.route("/login", methods=["GET", "POST"])
def login():
    if g.user:
        return redirect(url_for("dashboard"))
        
    if request.method == "POST":
        action = request.form.get("action")
        
        if action == "login":
            username = request.form.get("username", "").strip()
            password = request.form.get("password", "")
            
            user = User.query.filter_by(username=username).first()
            if not user:
                user = User.query.filter_by(email=username).first()
                
            if user and user.check_password(password):
                session["user_id"] = user.id
                flash("Logged in successfully!", "success")
                return redirect(url_for("dashboard"))
            else:
                flash("Invalid username/email or password.", "danger")
                
        elif action == "register":
            username = request.form.get("username", "").strip()
            email = request.form.get("email", "").strip()
            password = request.form.get("password", "")
            confirm_password = request.form.get("confirm_password", "")
            
            if not username or not email or not password:
                flash("All fields are required.", "danger")
            elif password != confirm_password:
                flash("Passwords do not match.", "danger")
            else:
                existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
                if existing_user:
                    flash("Username or email already registered.", "danger")
                else:
                    new_user = User(username=username, email=email)
                    new_user.set_password(password)
                    db.session.add(new_user)
                    db.session.commit()
                    session["user_id"] = new_user.id
                    flash("Account created and logged in successfully!", "success")
                    return redirect(url_for("dashboard"))
                    
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("login"))


@app.route("/")
def dashboard():

    total_students, high_risk_students, medium_risk_students, low_risk_students = get_risk_counts()
    pending_reports = Report.query.filter_by(status="Pending").count()

    high_risk_list = Student.query.filter_by(risk_label="High").order_by(Student.risk_score.desc()).limit(6).all()

    months, low_series, medium_series, high_series = get_trend_data()

    return render_template(
        "dashboard.html",
        total_students=total_students,
        pending_reports=pending_reports,
        high_risk_students=high_risk_students,
        medium_risk_students=medium_risk_students,
        low_risk_students=low_risk_students,
        high_risk_list=high_risk_list,
        trend_months=months,
        trend_low=low_series,
        trend_medium=medium_series,
        trend_high=high_series,
    )


@app.route("/students")
def students():

    query = request.args.get("q", "").strip()

    if query:
        students_list = Student.query.filter(Student.name.ilike(f"%{query}%")).all()
    else:
        students_list = Student.query.all()

    return render_template(
        "students.html",
        students=students_list,
        query=query
    )


@app.route("/add_student", methods=["GET", "POST"])
def add_student():

    if request.method == "POST":

        student = Student(
            name=request.form["name"],
            gpa=float(request.form["gpa"]),
            attendance=float(request.form["attendance"]),
            assignments_completed=int(request.form["assignments_completed"]),
            risk_score=0.0,
            risk_label="Low"
        )

        db.session.add(student)
        db.session.commit()

        return redirect(url_for("students"))

    return render_template("add_student.html")


@app.route("/edit_student/<int:student_id>", methods=["GET", "POST"])
def edit_student(student_id):

    student = Student.query.get_or_404(student_id)

    if request.method == "POST":
        student.name = request.form["name"]
        student.gpa = float(request.form["gpa"])
        student.attendance = float(request.form["attendance"])
        student.assignments_completed = int(request.form["assignments_completed"])

        db.session.commit()

        return redirect(url_for("students"))

    return render_template("edit_student.html", student=student)


@app.route("/delete_student/<int:student_id>", methods=["POST"])
def delete_student(student_id):

    student = Student.query.get_or_404(student_id)
    db.session.delete(student)
    db.session.commit()

    return redirect(url_for("students"))


@app.route("/reports")
def reports():

    reports_list = Report.query.all()

    return render_template(
        "reports.html",
        reports=reports_list
    )


@app.route("/high-risk")
def high_risk():

    students_list = Student.query.filter_by(risk_label="High").all()

    return render_template(
        "high_risk.html",
        students=students_list
    )


@app.route("/settings")
def settings():
    return render_template("settings.html")


@app.route("/export_csv")
def export_csv():

    students_list = Student.query.all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Name", "GPA", "Attendance", "Assignments Completed", "Risk Score", "Risk Label"])

    for s in students_list:
        writer.writerow([s.id, s.name, s.gpa, s.attendance, s.assignments_completed, s.risk_score, s.risk_label])

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=students_report.csv"}
    )


@app.route("/import_csv", methods=["POST"])
def import_csv():

    file = request.files.get("csv_file")

    if not file:
        return redirect(url_for("students"))

    stream = io.StringIO(file.stream.read().decode("utf-8"))
    reader = csv.DictReader(stream)

    for row in reader:
        try:
            student = Student(
                name=row.get("Name") or row.get("name"),
                gpa=float(row.get("GPA") or row.get("gpa") or 0),
                attendance=float(row.get("Attendance") or row.get("attendance") or 0),
                assignments_completed=int(row.get("Assignments Completed") or row.get("assignments_completed") or 0),
                risk_score=float(row.get("Risk Score") or row.get("risk_score") or 0),
                risk_label=row.get("Risk Label") or row.get("risk_label") or "Low"
            )
            db.session.add(student)
        except (TypeError, ValueError):
            continue

    db.session.commit()

    return redirect(url_for("students"))


@app.route("/api/students")
def api_students():

    query = request.args.get("q", "").strip()

    if query:
        students_list = Student.query.filter(Student.name.ilike(f"%{query}%")).all()
    else:
        students_list = Student.query.all()

    return jsonify([
        {
            "id": s.id,
            "name": s.name,
            "gpa": s.gpa,
            "attendance": s.attendance,
            "assignments_completed": s.assignments_completed,
            "risk_score": s.risk_score,
            "risk_label": s.risk_label
        }
        for s in students_list
    ])


if __name__ == "__main__":
    app.run(debug=True)
