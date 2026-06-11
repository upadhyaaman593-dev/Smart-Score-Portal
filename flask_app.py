from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# Railway PostgreSQL Connection Setup
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL or 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database Table Structure
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    roll_no = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    maths = db.Column(db.Integer, default=0)
    science = db.Column(db.Integer, default=0)
    english = db.Column(db.Integer, default=0)
    hindi = db.Column(db.Integer, default=0)
    sst = db.Column(db.Integer, default=0)
    total = db.Column(db.Integer)
    percentage = db.Column(db.String(10))
    status = db.Column(db.String(10))

# 1. स्टूडेंट होम पेज (सिर्फ रिजल्ट सर्च - कोई एडमिन लिंक नहीं)
@app.route("/", methods=["GET", "POST"])
def index():
    student = None
    error = None
    division = None
    if request.method == "POST":
        roll = request.form.get("roll_no", "").strip()
        student = Student.query.filter_by(roll_no=roll).first()
        
        if student:
            try:
                perc = float(student.percentage.replace('%', ''))
                if student.status == "FAIL":
                    division = "Fail"
                elif perc >= 60: division = "1st Division"
                elif perc >= 45: division = "2nd Division"
                elif perc >= 33: division = "3rd Division"
                else: division = "Fail"
            except:
                division = "N/A"
        else:
            error = "Roll Number नहीं मिला! कृपया सही रोल नंबर डालें।"
            
    return render_template("index.html", student=student, error=error, division=division)

# 2. सीक्रेट एडमिन रूट (/admin) - यहीं से मार्क्स एंट्री और डिलीट होगा
@app.route("/admin", methods=["GET", "POST"])
def admin():
    message = None
    if request.method == "POST":
        roll = request.form.get("roll_no", "").strip()
        name = request.form.get("name", "").strip()
        
        try:
            m = int(request.form.get("maths") or 0)
            s = int(request.form.get("science") or 0)
            e = int(request.form.get("english") or 0)
            h = int(request.form.get("hindi") or 0)
            st = int(request.form.get("sst") or 0)

            total = m + s + e + h + st
            per = round((total / 500) * 100, 2)
            
            if m < 33 or s < 33 or e < 33 or h < 33 or st < 33:
                res_status = "FAIL"
            else:
                res_status = "PASS" if per >= 33 else "FAIL"

            existing_student = Student.query.filter_by(roll_no=roll).first()
            if existing_student:
                student = existing_student
            else:
                student = Student(roll_no=roll)

            student.name = name
            student.maths, student.science, student.english = m, s, e
            student.hindi, student.sst = h, st
            student.total = total
            student.percentage = f"{per}%"
            student.status = res_status

            db.session.add(student)
            db.session.commit()
            message = f"✅ Success: {name} (Roll: {roll}) का रिजल्ट सुरक्षित सेव हो गया!"
        except Exception as ex:
            message = f"❌ Error: डेटा सेव नहीं हुआ। डिटेल: {str(ex)}"

    results = Student.query.all()
    return render_template("admin.html", message=message, results=results)

# 3. डिलीट रूट
@app.route("/delete/<roll_no>")
def delete_student(roll_no):
    student = Student.query.filter_by(roll_no=roll_no).first()
    if student:
        db.session.delete(student)
        db.session.commit()
    return redirect(url_for('admin'))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # डेटाबेस टेबल्स चेक/क्रिएट करना
    app.run(debug=True)
