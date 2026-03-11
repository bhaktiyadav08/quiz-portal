from flask import Flask, render_template, request, redirect, session
import sqlite3
from datetime import datetime

app = Flask("quiz_app")
app.secret_key = "secretkey"

def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT,
        password TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question TEXT,
        option1 TEXT,
        option2 TEXT,
        option3 TEXT,
        option4 TEXT,
        correct TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        score INTEGER,
        date TEXT
    )
    """)

    cursor.execute("SELECT COUNT(*) FROM questions")
    if cursor.fetchone()[0] == 0:
        sample_questions = [
            ("What is 20% of 200?", "20", "30", "40", "50", "40"),
            ("Profit on 100 selling at 120?", "10", "15", "20", "25", "20"),
            ("Ratio 2:4 equals?", "1:2", "2:1", "4:2", "3:4", "1:2"),
            ("15% of 300?", "30", "45", "60", "75", "45"),
            ("If SP=150, CP=100 Profit%?", "40%", "50%", "60%", "70%", "50%"),
            ("LCM of 4 and 6?", "12", "24", "6", "18", "12"),
            ("HCF of 8 and 12?", "2", "4", "6", "8", "4"),
            ("25% of 80?", "10", "15", "20", "25", "20"),
            ("Simple Interest on 1000 at 10% for 1 year?", "50", "100", "150", "200", "100"),
            ("Average of 10 and 20?", "10", "15", "20", "25", "15")
        ]
        cursor.executemany("""
        INSERT INTO questions (question, option1, option2, option3, option4, correct)
        VALUES (?, ?, ?, ?, ?, ?)
        """, sample_questions)

    conn.commit()
    conn.close()

@app.route("/")
def home():
    return redirect("/login")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                       (name, email, password))
        conn.commit()
        conn.close()
        return redirect("/login")
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            session["user_id"] = user[0]
            session["name"] = user[1]
            return redirect("/dashboard")
        else:
            return "Invalid Credentials"

    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/login")

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT score, date FROM results WHERE user_id=?", (session["user_id"],))
    results = cursor.fetchall()
    conn.close()

    return render_template("dashboard.html", name=session["name"], results=results)

@app.route("/quiz")
def quiz():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM questions LIMIT 10")
    questions = cursor.fetchall()
    conn.close()
    return render_template("quiz.html", questions=questions)

@app.route("/submit", methods=["POST"])
def submit():
    score = 0

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, correct FROM questions")
    questions = cursor.fetchall()

    for q in questions:
        selected = request.form.get(str(q[0]))
        if selected == q[1]:
            score += 1

    cursor.execute("INSERT INTO results (user_id, score, date) VALUES (?, ?, ?)",
                   (session["user_id"], score, datetime.now().strftime("%Y-%m-%d %H:%M")))
    conn.commit()
    conn.close()

    percentage = (score / 10) * 100
    return render_template("result.html", score=score, percentage=percentage)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
