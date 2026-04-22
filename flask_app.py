from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# Render PostgreSQL Connection String (DATABASE_URL aap Render se lenge)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database Table Setup
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    roll_no = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    maths = db.Column(db.Integer, default=0)
    science = db.Column(db.Integer, default=0)
    english = db.Column(db.Integer, default=0)
    hindi = db.Column(db.Integer, default=0)
    sst = db.Column(db.Integer, default=0)
    extra = db.Column(db.Integer, default=0)
    total = db.Column(db.Integer)
    percentage = db.Column(db.String(10))
    status = db.Column(db.String(10))

@app.route("/", methods=["GET", "POST"])
def index():
    student = None
    error = None
    division = None
    if request.method == "POST":
        roll = request.form.get("roll_no")
        student = Student.query.filter_by(roll_no=roll).first()
        
        if student:
            perc = float(student.percentage.replace('%', ''))
            if perc >= 60: division = "1st Division"
            elif perc >= 45: division = "2nd Division"
            elif perc >= 33: division = "3rd Division"
            else: division = "Fail"
        else:
            error = "Roll Number not found!"
            
    return render_template("index.html", student=student, error=error, division=division)

@app.route("/upload", methods=["GET", "POST"])
def upload_result():
    message = None
    if request.method == "POST":
        roll = request.form.get("roll_no")
        name = request.form.get("name")
        m = int(request.form.get("maths") or 0)
        s = int(request.form.get("science") or 0)
        e = int(request.form.get("english") or 0)
        h = int(request.form.get("hindi") or 0)
        st = int(request.form.get("sst") or 0)
        ex = int(request.form.get("extra") or 0)

        total = m + s + e + h + st + ex
        per = round((total / 500) * 100, 2)
        res_status = "PASS" if per >= 30 else "FAIL"

        # Check if student already exists to update, else create new
        existing_student = Student.query.filter_by(roll_no=roll).first()
        if existing_student:
            student = existing_student
        else:
            student = Student(roll_no=roll)

        student.name = name
        student.maths, student.science, student.english = m, s, e
        student.hindi, student.sst, student.extra = h, st, ex
        student.total = total
        student.percentage = f"{per}%"
        student.status = res_status

        db.session.add(student)
        db.session.commit()
        message = f"✅ Success: Result Saved for {name}!"

    return render_template("upload.html", message=message)

@app.route("/admin", methods=["GET", "POST"])
def admin():
    authorized = False
    results = []
    if request.method == "POST":
        if request.form.get("password") == "admin123":
            authorized = True
            results = Student.query.all()
    return render_template("admin.html", authorized=authorized, results=results)

@app.route("/delete/<roll_no>")
def delete_student(roll_no):
    student = Student.query.filter_by(roll_no=roll_no).first()
    if student:
        db.session.delete(student)
        db.session.commit()
    return redirect(url_for('admin'))

if __name__ == "__main__":
    with app.app_context():
        db.create_all() # Yeh line apne aap table bana degi
    app.run(debug=True)
  
