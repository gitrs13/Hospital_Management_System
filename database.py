import mysql.connector
from mysql.connector import Error

# ── Change these to match your MySQL setup ──────────────────
DB_HOST     = "localhost"
DB_USER     = "root"
DB_PASSWORD = "rs@mysql"      
DB_NAME     = "hospital_db"
# ────────────────────────────────────────────────────────────

def get_connection():
    """Return a fresh MySQL connection."""
    try:
        conn = mysql.connector.connect(
            host     = DB_HOST,
            user     = DB_USER,
            password = DB_PASSWORD,
            database = DB_NAME
        )
        return conn
    except Error as e:
        raise ConnectionError(f"Database connection failed: {e}")


# Shared connection used across the app
try:
    conn   = get_connection()
    cursor = conn.cursor()
    print("[DB] Connected to hospital_db successfully.")
except ConnectionError as e:
    print(e)
    conn   = None
    cursor = None
