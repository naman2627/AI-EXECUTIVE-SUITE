# db.py

import os
import sqlite3

DB_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DB_DIR, exist_ok=True)
DB_PATH = os.path.join(DB_DIR, "app.db")

conn = sqlite3.connect(DB_PATH, check_same_thread=False)
cursor = conn.cursor()

# users table
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT
)
""")

# chats table
cursor.execute("""
CREATE TABLE IF NOT EXISTS chats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    role TEXT,
    content TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

conn.commit()

def create_user(username, password):
    """Create a new user"""
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

def get_user(username, password):
    """Authenticate user"""
    cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    return cursor.fetchone()

def save_chat(user_id, role, content):
    """Save a chat message"""
    cursor.execute("INSERT INTO chats (user_id, role, content) VALUES (?, ?, ?)", (user_id, role, content))
    conn.commit()

def load_chats(user_id):
    """Load chat history for a user"""
    cursor.execute("SELECT role, content FROM chats WHERE user_id=? ORDER BY timestamp", (user_id,))
    return cursor.fetchall()
