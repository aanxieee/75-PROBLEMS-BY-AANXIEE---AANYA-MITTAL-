"""
Daily Food Tracker with SQLite Persistence
Handles food logging, user profiles, and data persistence across sessions.
"""
import sqlite3
import os
from datetime import datetime, date
from typing import List, Dict, Optional, Tuple

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "nutrition.db")


def get_connection() -> sqlite3.Connection:
    """Get SQLite connection, creating tables if needed."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    _create_tables(conn)
    return conn


def _create_tables(conn: sqlite3.Connection):
    """Create required tables if they don't exist."""
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS user_profile (
            id INTEGER PRIMARY KEY DEFAULT 1,
            name TEXT DEFAULT 'User',
            age INTEGER DEFAULT 25,
            gender TEXT DEFAULT 'female',
            weight_kg REAL DEFAULT 60,
            height_cm REAL DEFAULT 160,
            activity_level TEXT DEFAULT 'moderate',
            goal TEXT DEFAULT 'maintain',
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS food_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            meal_type TEXT NOT NULL,
            food_id TEXT NOT NULL,
            food_name TEXT NOT NULL,
            servings REAL DEFAULT 1.0,
            calories REAL DEFAULT 0,
            protein REAL DEFAULT 0,
            carbs REAL DEFAULT 0,
            fats REAL DEFAULT 0,
            fiber REAL DEFAULT 0,
            calcium REAL DEFAULT 0,
            iron REAL DEFAULT 0,
            zinc REAL DEFAULT 0,
            vitamin_a REAL DEFAULT 0,
            vitamin_b12 REAL DEFAULT 0,
            vitamin_c REAL DEFAULT 0,
            vitamin_d REAL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()


# ── User Profile ──────────────────────────────────────────────

def get_profile(conn: sqlite3.Connection) -> Optional[Dict]:
    """Get user profile. Returns None if not set up."""
    row = conn.execute("SELECT * FROM user_profile WHERE id = 1").fetchone()
    if row:
        return dict(row)
    return None


def save_profile(conn: sqlite3.Connection, name: str, age: int, gender: str,
                 weight_kg: float, height_cm: float, activity_level: str, goal: str) -> Dict:
    """Save or update user profile."""
    existing = get_profile(conn)
    if existing:
        conn.execute("""
            UPDATE user_profile SET name=?, age=?, gender=?, weight_kg=?,
            height_cm=?, activity_level=?, goal=?, updated_at=?
            WHERE id = 1
        """, (name, age, gender, weight_kg, height_cm, activity_level, goal, datetime.now()))
    else:
        conn.execute("""
            INSERT INTO user_profile (id, name, age, gender, weight_kg, height_cm, activity_level, goal, updated_at)
            VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, age, gender, weight_kg, height_cm, activity_level, goal, datetime.now()))
    conn.commit()
    return get_profile(conn)


# ── Food Log ─────────────────────────────────────────────────

def add_food_entry(conn: sqlite3.Connection, meal_type: str, food: Dict,
                   servings: float = 1.0, log_date: str = None) -> int:
    """Add a food entry to the log. Returns the new entry ID."""
    if log_date is None:
        log_date = date.today().isoformat()

    nutrients = food["nutrients"]
    cursor = conn.execute("""
        INSERT INTO food_log (date, meal_type, food_id, food_name, servings,
            calories, protein, carbs, fats, fiber,
            calcium, iron, zinc, vitamin_a, vitamin_b12, vitamin_c, vitamin_d)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        log_date, meal_type, food["id"], food["name"], servings,
        nutrients["calories"] * servings,
        nutrients["protein"] * servings,
        nutrients["carbs"] * servings,
        nutrients["fats"] * servings,
        nutrients["fiber"] * servings,
        nutrients["calcium"] * servings,
        nutrients["iron"] * servings,
        nutrients["zinc"] * servings,
        nutrients["vitamin_a"] * servings,
        nutrients["vitamin_b12"] * servings,
        nutrients["vitamin_c"] * servings,
        nutrients["vitamin_d"] * servings,
    ))
    conn.commit()
    return cursor.lastrowid


def get_daily_log(conn: sqlite3.Connection, log_date: str = None) -> List[Dict]:
    """Get all food entries for a specific date."""
    if log_date is None:
        log_date = date.today().isoformat()

    rows = conn.execute(
        "SELECT * FROM food_log WHERE date = ? ORDER BY created_at", (log_date,)
    ).fetchall()
    return [dict(r) for r in rows]


def get_daily_totals(conn: sqlite3.Connection, log_date: str = None) -> Dict:
    """Get total nutrients consumed for a specific date."""
    if log_date is None:
        log_date = date.today().isoformat()

    row = conn.execute("""
        SELECT
            COALESCE(SUM(calories), 0) as calories,
            COALESCE(SUM(protein), 0) as protein,
            COALESCE(SUM(carbs), 0) as carbs,
            COALESCE(SUM(fats), 0) as fats,
            COALESCE(SUM(fiber), 0) as fiber,
            COALESCE(SUM(calcium), 0) as calcium,
            COALESCE(SUM(iron), 0) as iron,
            COALESCE(SUM(zinc), 0) as zinc,
            COALESCE(SUM(vitamin_a), 0) as vitamin_a,
            COALESCE(SUM(vitamin_b12), 0) as vitamin_b12,
            COALESCE(SUM(vitamin_c), 0) as vitamin_c,
            COALESCE(SUM(vitamin_d), 0) as vitamin_d
        FROM food_log WHERE date = ?
    """, (log_date,)).fetchone()
    return dict(row)


def get_meal_totals(conn: sqlite3.Connection, log_date: str = None) -> Dict[str, Dict]:
    """Get nutrient totals broken down by meal type."""
    if log_date is None:
        log_date = date.today().isoformat()

    meals = {}
    for meal in ["Breakfast", "Lunch", "Snack", "Dinner"]:
        row = conn.execute("""
            SELECT
                COALESCE(SUM(calories), 0) as calories,
                COALESCE(SUM(protein), 0) as protein,
                COALESCE(SUM(carbs), 0) as carbs,
                COALESCE(SUM(fats), 0) as fats
            FROM food_log WHERE date = ? AND meal_type = ?
        """, (log_date, meal)).fetchone()
        meals[meal] = dict(row)
    return meals


def remove_food_entry(conn: sqlite3.Connection, entry_id: int) -> bool:
    """Remove a specific food entry by its ID."""
    cursor = conn.execute("DELETE FROM food_log WHERE id = ?", (entry_id,))
    conn.commit()
    return cursor.rowcount > 0


def get_log_dates(conn: sqlite3.Connection, limit: int = 7) -> List[str]:
    """Get the most recent dates that have log entries."""
    rows = conn.execute(
        "SELECT DISTINCT date FROM food_log ORDER BY date DESC LIMIT ?", (limit,)
    ).fetchall()
    return [r["date"] for r in rows]
