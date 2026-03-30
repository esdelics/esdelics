from flask import Flask, request, jsonify, session
import sqlite3
from flask_cors import CORS
from flask_bcrypt import Bcrypt

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.secret_key = "super_secret_key_change_this"

bcrypt = Bcrypt(app)
DB_NAME = "matches.db"

# ---------------- DATABASE INIT ----------------
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # Matches table
    c.execute('''
        CREATE TABLE IF NOT EXISTS matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            match_count TEXT,
            maps TEXT,
            day TEXT,
            date TEXT,
            room TEXT,
            time TEXT,
            entry_fee TEXT,
            prize1 TEXT,
            prize2 TEXT,
            prize3 TEXT,
            register_link TEXT
        )
    ''')

    # Admin table
    c.execute('''
        CREATE TABLE IF NOT EXISTS admin (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    ''')

    # ---------------- FORCEFULLY UPDATE ADMIN ----------------
    new_username = "Sumit ESD Boss"
    new_password_plain = "#@esDmydreamProject143Vaishnavi"
    hashed_pw = bcrypt.generate_password_hash(new_password_plain).decode('utf-8')

    # Check if admin exists
    c.execute("SELECT * FROM admin")
    if c.fetchone():
        # Update the first admin user
        c.execute("UPDATE admin SET username = ?, password = ? WHERE id = 1", (new_username, hashed_pw))
    else:
        # Create admin if table is empty
        c.execute("INSERT INTO admin (username, password) VALUES (?, ?)", (new_username, hashed_pw))

    conn.commit()
    conn.close()

init_db()

# ---------------- AUTH HELPER ----------------
def is_admin():
    return 'admin' in session

# ---------------- LOGIN ----------------
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM admin WHERE username = ?", (data.get("username"),))
    user = c.fetchone()
    conn.close()

    if user and bcrypt.check_password_hash(user[2], data.get("password")):
        session['admin'] = user[1]
        return jsonify({"message": "Login successful"})
    return jsonify({"message": "Invalid credentials"}), 401

# ---------------- LOGOUT ----------------
@app.route('/logout', methods=['POST'])
def logout():
    session.pop('admin', None)
    return jsonify({"message": "Logged out"})

# ---------------- ADD MATCH ----------------
@app.route('/add-match', methods=['POST'])
def add_match():
    if not is_admin():
        return jsonify({"message": "Unauthorized"}), 403

    data = request.get_json()
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("""
        INSERT INTO matches 
        (title, match_count, maps, day, date, room, time, entry_fee, prize1, prize2, prize3, register_link)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data.get('title'),
        data.get('match_count'),
        data.get('maps'),
        data.get('day'),
        data.get('date'),
        data.get('room'),
        data.get('time'),
        data.get('entry_fee'),
        data.get('prize1'),
        data.get('prize2'),
        data.get('prize3'),
        data.get('register_link')
    ))

    conn.commit()
    conn.close()
    return jsonify({"message": "Match added successfully"})

# ---------------- GET MATCHES ----------------
@app.route('/matches', methods=['GET'])
def get_matches():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM matches")
    rows = c.fetchall()
    conn.close()

    matches = []
    for row in rows:
        matches.append({
            "id": row[0],
            "title": row[1],
            "match_count": row[2],
            "maps": row[3],
            "day": row[4],
            "date": row[5],
            "room": row[6],
            "time": row[7],
            "entry_fee": row[8],
            "prize1": row[9],
            "prize2": row[10],
            "prize3": row[11],
            "register_link": row[12]
        })
    return jsonify(matches)

# ---------------- DELETE MATCH ----------------
@app.route('/delete-match/<int:id>', methods=['DELETE'])
def delete_match(id):
    if not is_admin():
        return jsonify({"message": "Unauthorized"}), 403

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM matches WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Match deleted"})

# ---------------- RUN ----------------
if __name__ == '__main__':
    app.run(debug=True)