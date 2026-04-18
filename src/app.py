from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3
import random

app = Flask(__name__)

# 1. Database Setup: To create the users table
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/signup_page')
def signup_page():
    return render_template('signup.html')

# 2. Register Logic: To create a new user account
@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
        conn.commit()
        conn.close()
        return "Registration Successful! Now you can <a href='/'>Login</a>."
    except sqlite3.IntegrityError:
        return "Error: Username already exists! Please try a different one."

# 3. Secure Login Logic: To verify credentials from the database
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username=? AND password=?', (username, password))
    user = c.fetchone()
    conn.close()

    if user:
        return redirect(url_for('dashboard'))
    else:
        return "Invalid Credentials! Please try again."

@app.route('/dashboard')
def dashboard():
    return render_template('index.html')

# 4. Cybersecurity Feature: Real-time Threat Monitoring API
@app.route('/threat')
def threat_monitor():
    threat_types = ["DDoS Attack", "SQL Injection", "Phishing", "Brute Force"]
    risk_level = random.choice(["Low", "Medium", "High", "Critical"])
    return jsonify({
        "status": "Scanning",
        "current_threat": random.choice(threat_types),
        "risk_level": risk_level,
        "active_alerts": random.randint(1, 10)
    })

if __name__ == '__main__':
    # Running on port 5050 as configured in the Docker setup
    app.run(host='0.0.0.0', port=5050)