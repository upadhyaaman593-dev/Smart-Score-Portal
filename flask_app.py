from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# रेलवे के PostgreSQL से ऑटोमैटिक कनेक्ट करने के लिए लिंक
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL or 'sqlite:///database.db'
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
    total = db.Column(db.Integer)
    percentage = db.Column(db.String(10))
    status = db.Column(db.String(10))

# 1. होम पेज (छात्रों के लिए रिजल्ट सर्च)
@app.route("/", methods=["GET", "POST"])
def index():
    student = None
    error = None
    division = None
    if request.method == "POST":
        roll = request.form.get("roll_no", "").strip()
        student = Student.query.filter_by(roll_no=roll).first()
        
        if student:
            # प्रतिशत से '%' हटाकर फ्लोट में बदलना डिवीजन चेक करने के लिए
            perc = float(student.percentage.replace('%', ''))
            if student.status == "FAIL":
                division = "Fail"
            elif perc >= 60: division = "1st Division"
            elif perc >= 45: division = "2nd Division"
            elif perc >= 33: division = "3rd Division"
            else: division = "Fail"
        else:
            error = "Roll Number नहीं मिला! कृपया सही रोल नंबर डालें।"
            
    return render_template("index.html", student=student, error=error, division=division)

# 2. नया एडमिन पैनल (यहीं से एंट्री होगी और यहीं लिस्ट दिखेगी)
@app.route("/admin", methods=["GET", "POST"])
def admin():
    message = None
    if request.method == "POST":
        roll = request.form.get("roll_no", "").strip()
        name = request.form.get("name", "").strip()
        m = int(request.form.get("maths") or 0)
        s = int(request.form.get("science") or 0)
        e = int(request.form.get("english") or 0)
        h = int(request.form.get("hindi") or 0)
        st = int(request.form.get("sst") or 0)

        # 5 मुख्य विषयों का टोटल (मैक्स मार्क्स = 500)
        total = m + s + e + h + st
        per = round((total / 500) * 100, 2)
        
        # पास/फेल कंडीशन (33 नंबर से कम होने पर फेल)
        if m < 33 or s < 33 or e < 33 or h < 33 or st < 33:
            res_status = "FAIL"
        else:
            res_status = "PASS" if per >= 33 else "FAIL"

        # अगर स्टूडेंट पहले से है तो अपडेट करें, नहीं तो नया बनाएं
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

    # डेटाबेस से सभी छात्रों की लिस्ट खींचना ताकि नीचे टेबल में दिखे
    results = Student.query.all()
    return render_template("admin.html", message=message, results=results)

# 3. स्टूडेंट डिलीट करने का लॉजिक
@app.route("/delete/<roll_no>")
def delete_student(roll_no):
    student = Student.query.filter_by(roll_no=roll_no).first()
    if student:
        db.session.delete(student)
        db.session.commit()
    return redirect(url_for('admin'))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # रेलवे पर खुद ही टेबल बना देगा
    app.run(debug=True)
