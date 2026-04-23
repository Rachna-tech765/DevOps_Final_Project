import logging
import os
import re
import sqlite3
import random
import time
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.urandom(24)
PORT = 5050

# --- CONFIGURATION ---
# Database Setup
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)')
    conn.commit()
    conn.close()

init_db()

# Reference Data
ips = ["192.168.1.157", "192.168.1.32", "192.168.1.94", "192.168.1.45"]
endpoints = ["/api/v1/auth", "/login", "/dashboard", "/admin/settings"]
threat_vectors = ["Healthy", "Brute Force", "SQL Injection", "XSS Attempt"]
threat_vectors_all = ["Healthy", "Brute Force", "SQL Injection", "XSS Attempt", "Invasive Scan"]


# --- REAL-TIME DATA SIMULATION LOGIC ---
# This mirrors the logic in the provided reference GitHub
def get_threat_data():
    # Simulate historical log data for charts
    history_data = []
    
    # Pre-defined fixed counts for consistency with dashboard view (e.g., Image 3)
    brute_force_events = 54
    sql_injection_events = 21
    invasive_scan_events = 12
    xss_attempt_events = 4
    healthy_events = 112
    
    # Calculate Severity distribution for Donut Chart
    critical_events = brute_force_events + sql_injection_events
    high_events = invasive_scan_events
    medium_events = xss_attempt_events
    
    # Build history for line chart (velocity)
    now = time.time()
    for i in range(20):
        t = now - (19-i) * 2
        velocity = random.uniform(8, 15) # Example req/s
        history_data.append({"time": t, "velocity": velocity})

    # Get recent logs for the table
    recent_logs = []
    for _ in range(10):
        source_ip = random.choice(ips)
        timestamp = datetime.fromtimestamp(now - random.uniform(0, 60)).strftime("%Y-%m-%d %H:%M:%S")
        endpoint = random.choice(endpoints)
        vector = random.choice(threat_vectors_all)
        recent_logs.append({
            "ip": source_ip,
            "timestamp": timestamp,
            "endpoint": endpoint,
            "vector": vector,
            "action": "-" if vector == "Healthy" else "Analyze"
        })

    return {
        "velocity": f"{history_data[-1]['velocity']:.1f}",
        "active_threats": 3,
        "history": history_data,
        "logs": recent_logs,
        "donut_data": [critical_events, high_events, medium_events], # Critical, High, Medium
        "cards_data": [brute_force_events, sql_injection_events, invasive_scan_events, xss_attempt_events] # For display
    }


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
        return "Error: Password must be 6+ chars & include @, # or $. <a href='/signup_page'>Try again</a>"

    hashed_pw = generate_password_hash(password, method='pbkdf2:sha256')
    
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_pw))
        conn.commit()
        conn.close()
        return "Signup Success! <a href='/'>Login now</a>"
    except sqlite3.IntegrityError:
        return "Username already exists! <a href='/signup_page'>Try again</a>"

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username=?', (username,))
    user = c.fetchone()
    conn.close()

    if user and check_password_hash(user['password'], password):
        session['username'] = username
        return redirect(url_for('dashboard'))
    else:
        return "Invalid username or password! <a href='/'>Try again</a>"

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('home'))
    return render_template('index.html', user=session['username'])

# The Core API that connects everything
@app.route('/api/telemetry')
def telemetry():
    if 'username' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    return jsonify(get_threat_data())

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT, debug=True)












# import logging
# import os
# import re
# import sqlite3
# import random
# from datetime import datetime
# from flask import Flask, render_template, request, redirect, url_for, jsonify, session
# from werkzeug.security import generate_password_hash, check_password_hash

# app = Flask(__name__)
# app.secret_key = os.urandom(24)

# # Database Setup
# def init_db():
#     conn = sqlite3.connect('users.db')
#     c = conn.cursor()
#     c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)')
#     conn.commit()
#     conn.close()

# init_db()

# # Main Routes
# @app.route('/')
# def home():
#     if 'username' in session:
#         return redirect(url_for('dashboard'))
#     return render_template('login.html')

# @app.route('/signup_page')
# def signup_page():
#     return render_template('signup.html')

# # Register Logic with Password Hashing
# @app.route('/register', methods=['POST'])
# def register():
#     username = request.form.get('username')
#     password = request.form.get('password')
    
#     # Simple validation for now
#     if not password or len(password) < 6:
#         return "Error: Password must be 6+ characters. <a href='/signup_page'>Back</a>"
    
#     hashed_pw = generate_password_hash(password, method='pbkdf2:sha256')
#     try:
#         conn = sqlite3.connect('users.db')
#         c = conn.cursor()
#         c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_pw))
#         conn.commit()
#         conn.close()
#         return "Signup Success! <a href='/'>Login now</a>"
#     except sqlite3.IntegrityError:
#         return "User exists!"

# @app.route('/login', methods=['POST'])
# def login():
#     username = request.form.get('username')
#     password = request.form.get('password')
#     conn = sqlite3.connect('users.db')
#     conn.row_factory = sqlite3.Row
#     c = conn.cursor()
#     c.execute('SELECT * FROM users WHERE username=?', (username,))
#     user = c.fetchone()
#     conn.close()
    
#     if user and check_password_hash(user['password'], password):
#         session['username'] = username
#         return redirect(url_for('dashboard'))
#     return "Invalid Credentials!"

# @app.route('/dashboard')
# def dashboard():
#     if 'username' not in session:
#         return redirect(url_for('home'))
#     return render_template('index.html', user=session['username'])

# # REAL-TIME LOGS DATA: Reference Image Like Structure
# @app.route('/api/threat_logs')
# def threat_logs():
#     if 'username' not in session:
#         return jsonify({"error": "Unauthorized"}), 401
        
#     ips = ["192.168.1.157", "192.168.1.32", "192.168.1.94", "192.168.1.45"]
#     endpoints = ["/api/v1/auth", "/login", "/register", "/threat"]
#     vectors = ["Healthy", "Brute Force", "XSS Attempt"]
    
#     # Simulating data on each fetch
#     data = []
#     for _ in range(5): # Fetching 5 latest logs
#         vector = random.choice(vectors)
#         timestamp = datetime.now().strftime("%I:%M:%S %p")
        
#         data.append({
#             "source_ip": random.choice(ips),
#             "timestamp": timestamp,
#             "endpoint": random.choice(endpoints),
#             "vector": vector,
#             "action": "-" if vector == "Healthy" else "Analyze"
#         })
        
#     return jsonify(data)

# @app.route('/logout')
# def logout():
#     session.pop('username', None)
#     return redirect(url_for('home'))

# if __name__ == '__main__':
#     # PORT and HOST exactly like Prachi's repo for CV matching
#     app.run(host='0.0.0.0', port=5000, debug=True)










# import logging
# import os
# import re
# import sqlite3
# import random
# from flask import Flask, render_template, request, redirect, url_for, jsonify, session
# from werkzeug.security import generate_password_hash, check_password_hash

# app = Flask(__name__)

# # --- CONFIGURATION ---
# app.secret_key = os.urandom(24) # Session encryption ke liye
# PORT = 5050

# # --- LOGGING SETUP ---
# # Ye file 'security.log' banayega aur terminal pe bhi error dikhayega
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s | %(levelname)s | %(message)s',
#     handlers=[
#         logging.FileHandler("security.log"),
#         logging.StreamHandler() # Isse error terminal mein bhi dikhega
#     ]
# )

# # --- DATABASE INIT ---
# def init_db():
#     try:
#         conn = sqlite3.connect('users.db')
#         c = conn.cursor()
#         c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)')
#         conn.commit()
#         conn.close()
#         logging.info("Database initialized successfully.")
#     except Exception as e:
#         logging.error(f"Database error: {e}")

# init_db()

# # --- ROUTES ---

# @app.route('/')
# def home():
#     if 'username' in session:
#         return redirect(url_for('dashboard'))
#     return render_template('login.html')

# @app.route('/signup_page')
# def signup_page():
#     return render_template('signup.html')

# @app.route('/register', methods=['POST'])
# def register():
#     username = request.form.get('username')
#     password = request.form.get('password')
    
#     # Validation: 6 chars + Special Char
#     if not password or len(password) < 6 or not re.search("[@#$]", password):
#         logging.warning(f"Registration rejected for {username}: Weak password.")
#         return "Error: Password must be 6+ chars & include @ or #. <a href='/signup_page'>Back</a>"

#     hashed_pw = generate_password_hash(password, method='pbkdf2:sha256')
    
#     try:
#         conn = sqlite3.connect('users.db')
#         c = conn.cursor()
#         c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_pw))
#         conn.commit()
#         conn.close()
#         logging.info(f"New user registered: {username}")
#         return "Signup Success! <a href='/'>Login now</a>"
#     except sqlite3.IntegrityError:
#         return "Username already exists! <a href='/signup_page'>Try again</a>"

# @app.route('/login', methods=['POST'])
# def login():
#     username = request.form.get('username')
#     password = request.form.get('password')
    
#     try:
#         conn = sqlite3.connect('users.db')
#         conn.row_factory = sqlite3.Row
#         c = conn.cursor()
#         c.execute('SELECT * FROM users WHERE username=?', (username,))
#         user = c.fetchone()
#         conn.close()

#         if user and check_password_hash(user['password'], password):
#             session['username'] = username
#             logging.info(f"User login successful: {username}")
#             return redirect(url_for('dashboard'))
#         else:
#             logging.warning(f"Failed login attempt for: {username}")
#             return "Invalid username or password! <a href='/'>Try again</a>"
#     except Exception as e:
#         logging.error(f"Login Error: {e}")
#         return "System Error. Please check logs."

# @app.route('/dashboard')
# def dashboard():
#     if 'username' not in session:
#         logging.warning("Unauthorized dashboard access attempt.")
#         return redirect(url_for('home'))
#     return render_template('index.html', user=session['username'])

# @app.route('/threat')
# def threat_monitor():
#     if 'username' not in session:
#         return jsonify({"error": "Unauthorized"}), 401
    
#     threats = ["DDoS Attack", "SQL Injection", "Brute Force", "Port Scan"]
#     selected_threat = random.choice(threats)
    
#     # Real-time logging of threats
#     logging.critical(f"ALERT: {selected_threat} detected from {request.remote_addr}")
    
#     return jsonify({
#         "status": "Scanning",
#         "current_threat": selected_threat,
#         "risk_level": random.choice(["Medium", "High", "Critical"]),
#         "active_alerts": random.randint(1, 10)
#     })

# @app.route('/logout')
# def logout():
#     user = session.get('username')
#     session.pop('username', None)
#     logging.info(f"User logged out: {user}")
#     return redirect(url_for('home'))

# if __name__ == '__main__':
#     print(f"--- Server starting on http://localhost:{PORT} ---")
#     app.run(host='0.0.0.0', port=PORT, debug=True)










