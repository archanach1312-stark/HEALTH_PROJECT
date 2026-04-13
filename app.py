from flask import Flask, render_template, request, redirect, session
import pickle
import pandas as pd
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "secret123"

# ---------------- LOAD FILES ----------------
model = pickle.load(open("model.pkl", "rb"))
cols = pickle.load(open("columns.pkl", "rb"))
accuracy = pickle.load(open("accuracy.pkl", "rb"))

DB_PATH = "health.db"

# ---------------- INIT DB ----------------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute('''
    CREATE TABLE IF NOT EXISTS records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        age REAL,
        gender TEXT,
        bp REAL,
        cholesterol REAL,
        glucose REAL,
        smoking INTEGER,
        alcohol INTEGER,
        exercise INTEGER,
        bmi REAL,
        family INTEGER,
        result TEXT
    )
    ''')

    conn.commit()
    conn.close()

init_db()

# ---------------- SAVE DATA ----------------
def save_to_db(data):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute('''
    INSERT INTO records 
    (age, gender, bp, cholesterol, glucose, smoking, alcohol, exercise, bmi, family, result)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', data)

    conn.commit()
    conn.close()

# ---------------- CHART DATA ----------------
def get_chart_data():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("SELECT age, bp, bmi FROM records ORDER BY id DESC LIMIT 10")
    data = c.fetchall()
    conn.close()

    data = data[::-1]

    ages = [d[0] for d in data]
    bp = [d[1] for d in data]
    bmi = [d[2] for d in data]

    return ages, bp, bmi

# ---------------- HEALTH SCORE ----------------
def calculate_score(bp, cholesterol, glucose, smoking, alcohol, exercise, bmi, family):
    score = 100

    if smoking == 1:
        score -= 15
    if alcohol == 1:
        score -= 10
    if bmi > 30:
        score -= 20
    if bp > 140:
        score -= 15
    if cholesterol > 240:
        score -= 15
    if glucose > 140:
        score -= 15
    if exercise == 0:
        score -= 10
    if family == 1:
        score -= 10

    return max(score, 10)

# ---------------- LOGIN ----------------
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == "admin" and request.form['password'] == "1234":
            session['user'] = "admin"
            return redirect('/home')
        else:
            return render_template("login.html", error="Invalid login ❌")

    return render_template("login.html")

# ---------------- HOME ----------------
@app.route('/home')
def home():
    if 'user' not in session:
        return redirect('/')

    ages, bp, bmi = get_chart_data()

    return render_template("index.html",
                           ages=ages,
                           bp=bp,
                           bmi=bmi,
                           accuracy=round(accuracy * 100, 2))

# ---------------- PREDICT ----------------
@app.route('/predict', methods=['POST'])
def predict():
    if 'user' not in session:
        return redirect('/')

    try:
        age = float(request.form['Age'])
        gender = request.form['Gender']
        bp = float(request.form['Blood Pressure'])
        cholesterol = float(request.form['Cholesterol'])
        glucose = float(request.form['Glucose'])
        smoking = int(request.form['Smoking'])
        alcohol = int(request.form['Alcohol Consumption'])
        exercise = int(request.form['Exercise'])
        bmi = float(request.form['BMI'])
        family = int(request.form['Family History'])

        df = pd.DataFrame([{
            'Age': age,
            'Gender': gender,
            'Blood Pressure': bp,
            'Cholesterol': cholesterol,
            'Glucose': glucose,
            'Smoking': smoking,
            'Alcohol Consumption': alcohol,
            'Exercise': exercise,
            'BMI': bmi,
            'Family History': family
        }])

        df = pd.get_dummies(df)
        df = df.reindex(columns=cols, fill_value=0)

        pred = model.predict(df)[0]
        result = "High Risk ⚠️" if pred == 1 else "Normal ✅"

        score = calculate_score(bp, cholesterol, glucose, smoking, alcohol, exercise, bmi, family)

        save_to_db((age, gender, bp, cholesterol, glucose,
                    smoking, alcohol, exercise, bmi, family, result))

    except Exception as e:
        print("ERROR:", e)
        result = "Error ❌"
        score = 0

    ages, bp, bmi = get_chart_data()

    return render_template("index.html",
                           prediction_text=result,
                           score=score,
                           ages=ages,
                           bp=bp,
                           bmi=bmi,
                           accuracy=round(accuracy * 100, 2))

# ---------------- HISTORY ----------------
@app.route('/history')
def history():
    if 'user' not in session:
        return redirect('/')

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM records ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()

    return render_template("history.html", records=rows)

# ---------------- LOGOUT ----------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# ---------------- RUN ----------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)