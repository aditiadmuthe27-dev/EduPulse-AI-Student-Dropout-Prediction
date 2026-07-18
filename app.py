import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user

from extensions import db, login_manager, bcrypt
from models import User, Student, Report
import ml_model


app = Flask(__name__)

app.config["SECRET_KEY"] = "secret_key_123"

basedir = os.path.abspath(os.path.dirname(__file__))

app.config["SQLALCHEMY_DATABASE_URI"] = (
    "sqlite:///" + os.path.join(basedir, "edupulse.db")
)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.config["UPLOAD_FOLDER"] = os.path.join(
    basedir,
    "uploads"
)

os.makedirs(
    app.config["UPLOAD_FOLDER"],
    exist_ok=True
)

db.init_app(app)
login_manager.init_app(app)
bcrypt.init_app(app)

login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/")
def home():
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(
            username=username
        ).first()

        if user:
            flash("Username already exists")
            return redirect(url_for("register"))

        hashed_password = bcrypt.generate_password_hash(
            password
        ).decode("utf-8")

        new_user = User(
            username=username,
            email=email,
            password_hash=hashed_password,
            role="Student"
        )

        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful")

        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():

    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(
            username=username
        ).first()

        if user and bcrypt.check_password_hash(
            user.password_hash,
            password
        ):

            login_user(user)

            return redirect(
                url_for("dashboard")
            )

        flash("Invalid username or password")

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():

    logout_user()

    return redirect(
        url_for("login")
    )


@app.route("/dashboard")
@login_required
def dashboard():

    total_students = Student.query.count()

    pending_reports = Report.query.filter_by(
        status="Pending"
    ).count()

    high_risk_students = Student.query.filter_by(
        risk_label="High"
    ).count()

    return render_template(
        "dashboard.html",
        total_students=total_students,
        pending_reports=pending_reports,
        high_risk_students=high_risk_students
    )
@app.route("/add_student", methods=["GET", "POST"])
@login_required
def add_student():

    if request.method == "POST":

        student = Student(

            name=request.form["name"],

            gpa=float(
                request.form["gpa"]
            ),

            attendance=float(
                request.form["attendance"]
            ),

            assignments_completed=int(
                request.form["assignments_completed"]
            ),

            risk_label="Unknown",

            risk_score=0

        )

        db.session.add(student)
        db.session.commit()

        flash("Student added successfully")

        return redirect(
            url_for("dashboard")
        )

    return render_template(
        "add_student.html"
    )


@app.route("/students")
@login_required
def students():

    students = Student.query.all()

    return render_template(
        "students.html",
        students=students
    )


@app.route("/predict/<int:id>")
@login_required
def predict(id):

    student = Student.query.get(id)

    if not student:
        flash("Student not found")
        return redirect(
            url_for("dashboard")
        )

    risk_label, confidence = ml_model.predict_risk(
        student.gpa,
        student.attendance,
        student.assignments_completed
    )

    student.risk_label = risk_label
    student.risk_score = confidence

    report = Report(
        student_id=student.id,
        status="Generated",
        confidence_score=confidence
    )

    db.session.add(report)
    db.session.commit()

    flash(
        f"Prediction: {risk_label} ({confidence:.2f}%)"
    )

    return redirect(
        url_for("dashboard")
    )
@app.route("/reports")
@login_required
def reports():

    reports = Report.query.all()

    return render_template(
        "reports.html",
        reports=reports
    )


@app.route("/analytics")
@login_required
def analytics():

    low = Student.query.filter_by(
        risk_label="Low"
    ).count()

    medium = Student.query.filter_by(
        risk_label="Medium"
    ).count()

    high = Student.query.filter_by(
        risk_label="High"
    ).count()

    data = [
        low,
        medium,
        high
    ]

    return render_template(
        "analytics.html",
        chart_data=data
    )


@app.route("/high_risk")
@login_required
def high_risk():

    students = Student.query.filter_by(
        risk_label="High"
    ).all()

    return render_template(
        "high_risk.html",
        students=students
    )


@app.route("/upload_csv", methods=["GET", "POST"])
@login_required
def upload_csv():

    if request.method == "POST":

        if "file" not in request.files:
            flash("No file selected")
            return redirect(request.url)

        file = request.files["file"]

        if file.filename == "":
            flash("No file selected")
            return redirect(request.url)

        if file.filename.endswith(".csv"):

            filename = file.filename

            path = os.path.join(
                app.config["UPLOAD_FOLDER"],
                filename
            )

            file.save(path)

            try:
                ml_model.train_model(path)
                flash("Model trained successfully")

            except Exception as e:
                flash(str(e))

            return redirect(url_for("analytics"))

    return render_template(
        "upload_csv.html"
    )
@app.route("/profile")
@login_required
def profile():

    return render_template(
        "profile.html"
    )


@app.route("/settings")
@login_required
def settings():

    return render_template(
        "settings.html"
    )


@app.route("/api/v1/predict", methods=["POST"])
@login_required
def api_predict():

    data = request.json

    if not all(
        key in data
        for key in [
            "gpa",
            "attendance",
            "assignments_completed"
        ]
    ):

        return jsonify(
            {
                "error": "Missing data"
            }
        ), 400

    risk, confidence = ml_model.predict_risk(

        data["gpa"],
        data["attendance"],
        data["assignments_completed"]

    )

    return jsonify(
        {
            "risk_label": risk,
            "confidence_score": confidence
        }
    )


if __name__ == "__main__":

    with app.app_context():
        db.create_all()

    app.run(
        debug=True
    )