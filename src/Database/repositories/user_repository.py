from Database.database import get_connection
from datetime import datetime, timezone


def upsert_user(id: str, email: str, name: str = '', picture: str = '', google_token: str = '') -> dict:
    conn = get_connection()
    now = datetime.now(timezone.utc).isoformat()
    conn.execute(
        '''INSERT INTO users (id, email, name, picture, google_token, created_at)
           VALUES (?, ?, ?, ?, ?, ?)
           ON CONFLICT(email) DO UPDATE SET
               name=excluded.name,
               picture=excluded.picture,
               google_token=excluded.google_token''',
        (id, email, name, picture, google_token, now)
    )
    conn.commit()
    row = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
    conn.close()
    return dict(row)


def get_user_by_email(email: str) -> dict | None:
    conn = get_connection()
    row = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
    conn.close()
    return dict(row) if row else None


def get_current_session() -> dict | None:
    """Returns the most recently authenticated user (single-user CLI session)."""
    conn = get_connection()
    row = conn.execute(
        'SELECT * FROM users WHERE google_token IS NOT NULL AND google_token != "" ORDER BY created_at DESC LIMIT 1'
    ).fetchone()
    conn.close()
    return dict(row) if row else None
