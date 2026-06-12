from Database.database import get_connection
from datetime import datetime, timezone


def create_acceptance_criteria(id: str, requirement_id: str, content: str, author: str = '') -> dict:
    conn = get_connection()
    now = datetime.now(timezone.utc).isoformat()
    conn.execute(
        'INSERT INTO acceptance_criteria (id, requirement_id, content, author, created_at) VALUES (?, ?, ?, ?, ?)',
        (id, requirement_id, content, author, now)
    )
    conn.commit()
    conn.close()
    return {'id': id, 'requirement_id': requirement_id, 'content': content, 'author': author, 'created_at': now}


def get_acceptance_criteria_by_id(id: str) -> dict | None:
    conn = get_connection()
    row = conn.execute('SELECT * FROM acceptance_criteria WHERE id = ?', (id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def update_acceptance_criteria(id: str, content: str, author: str = '') -> bool:
    conn = get_connection()
    cur = conn.execute(
        'UPDATE acceptance_criteria SET content = ?, author = ? WHERE id = ?',
        (content, author, id)
    )
    conn.commit()
    conn.close()
    return cur.rowcount > 0


def delete_acceptance_criteria(id: str) -> bool:
    conn = get_connection()
    cur = conn.execute('DELETE FROM acceptance_criteria WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return cur.rowcount > 0


def list_acceptance_criteria_by_requirement(requirement_id: str) -> list[dict]:
    conn = get_connection()
    rows = conn.execute(
        'SELECT * FROM acceptance_criteria WHERE requirement_id = ? ORDER BY created_at ASC',
        (requirement_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
