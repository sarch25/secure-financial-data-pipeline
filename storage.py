import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone


def now():
    return datetime.now(timezone.utc).isoformat()


@contextmanager
def connect():
    path = os.environ.get('DATABASE_PATH', 'events.db')
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    conn = sqlite3.connect(path, timeout=10)
    conn.row_factory = sqlite3.Row
    try:
        with conn:
            yield conn
    finally:
        conn.close()


def initialize():
    with connect() as db:
        db.execute('''CREATE TABLE IF NOT EXISTS events (
            event_id TEXT PRIMARY KEY, symbol TEXT NOT NULL,
            event_type TEXT NOT NULL, price REAL NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending', created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL)''')
        db.execute('''CREATE TABLE IF NOT EXISTS audit (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id TEXT NOT NULL, action TEXT NOT NULL,
            occurred_at TEXT NOT NULL)''')


def create_event(data):
    timestamp = now()
    with connect() as db:
        try:
            db.execute('INSERT INTO events (event_id,symbol,event_type,price,status,created_at,updated_at) VALUES (?,?,?,?,?,?,?)',
                       (data['event_id'], data['symbol'], data['event_type'], data['price'], 'pending', timestamp, timestamp))
            db.execute('INSERT INTO audit (event_id,action,occurred_at) VALUES (?,?,?)', (data['event_id'], 'created', timestamp))
            return True
        except sqlite3.IntegrityError:
            return False


def get_event(event_id):
    with connect() as db:
        row = db.execute('SELECT * FROM events WHERE event_id=?', (event_id,)).fetchone()
        return dict(row) if row else None


def decide(event_id, action):
    with connect() as db:
        timestamp = now()
        cursor = db.execute('UPDATE events SET status=?, updated_at=? WHERE event_id=? AND status=?',
                            (action, timestamp, event_id, 'pending'))
        if cursor.rowcount:
            db.execute('INSERT INTO audit (event_id,action,occurred_at) VALUES (?,?,?)', (event_id, action, timestamp))
            return 'updated'
        exists = db.execute('SELECT 1 FROM events WHERE event_id=?', (event_id,)).fetchone()
        return 'conflict' if exists else 'missing'


def get_audit(event_id):
    with connect() as db:
        return [dict(row) for row in db.execute('SELECT action,occurred_at FROM audit WHERE event_id=? ORDER BY id', (event_id,))]
