# =========================
# src/app.py (Cybersecurity Backend)
# =========================
from flask import Flask, jsonify, send_from_directory
import random, datetime

app = Flask(__name__)

@app.route('/')
def login_page():
    return send_from_directory('static', 'login.html')

@app.route('/dashboard')
def dashboard():
    return send_from_directory('static', 'index.html')

@app.route('/threat')
def threat():
    # simulate realistic spikes
    if random.random() > 0.8:
        threats = random.randint(8, 12)
    else:
        threats = random.randint(0, 5)

    if threats > 7:
        level = "critical"
    elif threats > 3:
        level = "medium"
    else:
        level = "low"

    return jsonify({
        "status": level,
        "active_threats": threats,
        "blocked_ips": random.randint(20, 100),
        "attack_type": random.choice(["DDoS", "Brute Force", "SQL Injection", "Phishing"]),
        "last_updated": datetime.datetime.now().strftime("%I:%M:%S %p")
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
