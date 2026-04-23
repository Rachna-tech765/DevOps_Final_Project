import logging
import os
import re
import sqlite3
import random
from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# --- CONFIGURATION ---
app.secret_key = os.urandom(24) # Session encryption ke liye
PORT = 5050

# --- LOGGING SETUP ---
# Ye file 'security.log' banayega aur terminal pe bhi error dikhayega
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[
        logging.FileHandler("security.log"),
        logging.StreamHandler() # Isse error terminal mein bhi dikhega
    ]
)

# --- DATABASE INIT ---
def init_db():
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)')
        conn.commit()
        conn.close()
        logging.info("Database initialized successfully.")
    except Exception as e:
        logging.error(f"Database error: {e}")

init_db()

# --- ROUTES ---

@app.route('/')
def home():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/signup_page')
def signup_page():
    return render_template('signup.html')

@app.route('/register', methods=['POST'])
def register():
    username = request.form.get('username')
    password = request.form.get('password')
    
    # Validation: 6 chars + Special Char
    if not password or len(password) < 6 or not re.search("[@#$]", password):
        logging.warning(f"Registration rejected for {username}: Weak password.")
        return "Error: Password must be 6+ chars & include @ or #. <a href='/signup_page'>Back</a>"

    hashed_pw = generate_password_hash(password, method='pbkdf2:sha256')
    
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_pw))
        conn.commit()
        conn.close()
        logging.info(f"New user registered: {username}")
        return "Signup Success! <a href='/'>Login now</a>"
    except sqlite3.IntegrityError:
        return "Username already exists! <a href='/signup_page'>Try again</a>"

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    
    try:
        conn = sqlite3.connect('users.db')
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE username=?', (username,))
        user = c.fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['username'] = username
            logging.info(f"User login successful: {username}")
            return redirect(url_for('dashboard'))
        else:
            logging.warning(f"Failed login attempt for: {username}")
            return "Invalid username or password! <a href='/'>Try again</a>"
    except Exception as e:
        logging.error(f"Login Error: {e}")
        return "System Error. Please check logs."

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        logging.warning("Unauthorized dashboard access attempt.")
        return redirect(url_for('home'))
    return render_template('index.html', user=session['username'])

@app.route('/threat')
def threat_monitor():
    if 'username' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    threats = ["DDoS Attack", "SQL Injection", "Brute Force", "Port Scan"]
    selected_threat = random.choice(threats)
    
    # Real-time logging of threats
    logging.critical(f"ALERT: {selected_threat} detected from {request.remote_addr}")
    
    return jsonify({
        "status": "Scanning",
        "current_threat": selected_threat,
        "risk_level": random.choice(["Medium", "High", "Critical"]),
        "active_alerts": random.randint(1, 10)
    })

@app.route('/logout')
def logout():
    user = session.get('username')
    session.pop('username', None)
    logging.info(f"User logged out: {user}")
    return redirect(url_for('home'))

if __name__ == '__main__':
    print(f"--- Server starting on http://localhost:{PORT} ---")
    app.run(host='0.0.0.0', port=PORT, debug=True)
