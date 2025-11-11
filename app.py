from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
import os

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "defaultsecret")

# ---- DATABASE CONFIG USING ENV VARIABLES ----
db_config = {
    "host": os.getenv("DB_HOST", "sql12.freesqldatabase.com"),
    "user": os.getenv("DB_USER", "sql12807258"),
    "password": os.getenv("DB_PASSWORD", "tueQ4wZzzc"),  # your fallback password
    "database": os.getenv("DB_NAME", "sql12807258"),
    "port": int(os.getenv("DB_PORT", 3306))
}

try:
    db = mysql.connector.connect(**db_config)
    cursor = db.cursor(dictionary=True)
    print("✅ Database connected successfully")
except mysql.connector.Error as err:
    print("❌ Database connection failed:", err)

# ---- ROUTES ----
@app.route('/')
def index():
    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()

    cursor.execute("SELECT * FROM subjects")
    subjects = cursor.fetchall()

    cursor.execute("SELECT * FROM exams")
    exams = cursor.fetchall()

    cursor.execute("""
        SELECT r.result_id, s.full_name, sub.subject_name, e.exam_name, r.marks_obtained, r.grade 
        FROM results r
        JOIN students s ON r.student_id = s.student_id
        JOIN subjects sub ON r.subject_id = sub.subject_id
        JOIN exams e ON r.exam_id = e.exam_id
        ORDER BY r.result_id DESC
    """)
    results = cursor.fetchall()

    return render_template("index.html", students=students, subjects=subjects, exams=exams, results=results)

# ---- ADD STUDENT ----
@app.route('/add_student', methods=['POST'])
def add_student():
    roll_no = request.form['roll_no']
    full_name = request.form['full_name']
    dob = request.form['dob']
    email = request.form['email']
    school_name = request.form['school_name']
    grade_level = request.form['grade_level']

    cursor.execute("""
        INSERT INTO students (roll_no, full_name, dob, email, school_name, grade_level)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (roll_no, full_name, dob, email, school_name, grade_level))
    db.commit()

    flash("✅ Student added successfully!")
    return redirect(url_for('index'))

# ---- ADD RESULT (with text-based exam & subject) ----
@app.route('/add_result', methods=['POST'])
def add_result():
    student_id = request.form['student_id']
    exam_name = request.form['exam_name'].strip()
    subject_name = request.form['subject_name'].strip()
    marks = request.form['marks_obtained']
    grade = request.form['grade']
    remarks = request.form['remarks']

    # --- Handle Exam ---
    cursor.execute("SELECT exam_id FROM exams WHERE exam_name = %s", (exam_name,))
    exam = cursor.fetchone()
    if exam:
        exam_id = exam['exam_id']
    else:
        cursor.execute("INSERT INTO exams (exam_name, exam_date) VALUES (%s, CURDATE())", (exam_name,))
        db.commit()
        exam_id = cursor.lastrowid

    # --- Handle Subject ---
    cursor.execute("SELECT subject_id FROM subjects WHERE subject_name = %s", (subject_name,))
    subject = cursor.fetchone()
    if subject:
        subject_id = subject['subject_id']
    else:
        subject_code = subject_name[:5].upper()
        cursor.execute("INSERT INTO subjects (subject_code, subject_name) VALUES (%s, %s)", (subject_code, subject_name))
        db.commit()
        subject_id = cursor.lastrowid

    # --- Insert Result ---
    cursor.execute("""
        INSERT INTO results (student_id, exam_id, subject_id, marks_obtained, grade, remarks)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (student_id, exam_id, subject_id, marks, grade, remarks))
    db.commit()

    flash("✅ Result added successfully!")
    return redirect(url_for('index'))

# ---- RUN APP ----
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
