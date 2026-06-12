from Database.database import get_connection
from datetime import datetime, timezone


def create_persona(id: str, project_id: str, name: str, opportunities: str = '',
                   key_attributes: str = '', description: str = '',
                   needs: str = '', challenges: str = '') -> dict:
    conn = get_connection()
    now = datetime.now(timezone.utc).isoformat()
    conn.execute(
        '''INSERT INTO personas
           (id, project_id, name, opportunities, key_attributes, description, needs, challenges, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
        (id, project_id, name, opportunities, key_attributes, description, needs, challenges, now)
    )
    conn.commit()
    conn.close()
    return {
        'id': id, 'project_id': project_id, 'name': name,
        'opportunities': opportunities, 'key_attributes': key_attributes,
        'description': description, 'needs': needs, 'challenges': challenges,
        'created_at': now
    }


def get_persona_by_id(id: str) -> dict | None:
    conn = get_connection()
    row = conn.execute('SELECT * FROM personas WHERE id = ?', (id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def list_personas_by_project(project_id: str) -> list[dict]:
    conn = get_connection()
    rows = conn.execute(
        'SELECT * FROM personas WHERE project_id = ? ORDER BY created_at DESC', (project_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def update_persona(id: str, name: str, opportunities: str, key_attributes: str,
                   description: str, needs: str, challenges: str) -> bool:
    conn = get_connection()
    cur = conn.execute(
        '''UPDATE personas SET name=?, opportunities=?, key_attributes=?,
           description=?, needs=?, challenges=? WHERE id=?''',
        (name, opportunities, key_attributes, description, needs, challenges, id)
    )
    conn.commit()
    conn.close()
    return cur.rowcount > 0


def delete_persona(id: str) -> bool:
    conn = get_connection()
    conn.execute('DELETE FROM requirement_personas WHERE persona_id = ?', (id,))
    cur = conn.execute('DELETE FROM personas WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return cur.rowcount > 0
