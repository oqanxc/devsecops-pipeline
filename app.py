import sqlite3
from flask import Flask, request, jsonify

app = Flask(__name__)

# ⚠️ RISK 1: Hardcoded Secret Key (Secret Scanning yakalayacak)
SECRET_KEY = "super_secret_api_key_123456789"
DATABASE = "test.db"

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)")
    cursor.execute("INSERT OR IGNORE INTO users VALUES (1, 'admin', 'AdminPassword123!')")
    conn.commit()
    conn.close()

@app.route("/")
def home():
    return jsonify({"status": "running", "service": "DevSecOps Demo API"})

# ⚠️ RISK 2: SQL Injection (SAST / Bandit yakalayacak)
@app.route("/user", methods=["GET"])
def get_user():
    username = request.args.get("username", "")
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Zafiyetli Sorgu: Parametrik sorgu (?) kullanılmadı!
    query = f"SELECT id, username FROM users WHERE username = '{username}'"
    print(f"[LOG] Executing Query: {query}")
    
    try:
        cursor.execute(query)
        user = cursor.fetchone()
        conn.close()
        if user:
            return jsonify({"id": user[0], "username": user[1]})
        return jsonify({"message": "User not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)