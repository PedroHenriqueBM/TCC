from Database.database import get_connection
from datetime import datetime, timezone


def create_project(id: str, name: str, description: str, status: str = 'active') -> dict:
    conn = get_connection()
    now = datetime.now(timezone.utc).isoformat()
    conn.execute(
        'INSERT INTO projects (id, name, description, status, created_at) VALUES (?, ?, ?, ?, ?)',
        (id, name, description, status, now)
    )
    conn.commit()
    conn.close()
    return {'id': id, 'name': name, 'description': description, 'status': status, 'created_at': now}


def get_project_by_id(id: str) -> dict | None:
    conn = get_connection()
    row = conn.execute('SELECT * FROM projects WHERE id = ?', (id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def list_projects() -> list[dict]:
    conn = get_connection()
    rows = conn.execute('SELECT * FROM projects ORDER BY created_at DESC').fetchall()
    conn.close()
    return [dict(r) for r in rows]


def project_exists(id: str) -> bool:
    conn = get_connection()
    row = conn.execute('SELECT 1 FROM projects WHERE id = ?', (id,)).fetchone()
    conn.close()
    return row is not None


def update_project(id: str, name: str, description: str) -> bool:
    conn = get_connection()
    cur = conn.execute(
        'UPDATE projects SET name = ?, description = ? WHERE id = ?',
        (name, description, id)
    )
    conn.commit()
    conn.close()
    return cur.rowcount > 0


def delete_project(id: str) -> bool:
    conn = get_connection()
    conn.execute('DELETE FROM requirement_personas WHERE requirement_id IN (SELECT id FROM functional_requirements WHERE project_id = ?)', (id,))
    conn.execute('DELETE FROM acceptance_criteria WHERE requirement_id IN (SELECT id FROM functional_requirements WHERE project_id = ?)', (id,))
    conn.execute('DELETE FROM usability_inspection_executions WHERE requirement_id IN (SELECT id FROM functional_requirements WHERE project_id = ?)', (id,))
    conn.execute('DELETE FROM system_test_executions WHERE requirement_id IN (SELECT id FROM functional_requirements WHERE project_id = ?)', (id,))
    conn.execute('DELETE FROM comments WHERE entity_id IN (SELECT id FROM functional_requirements WHERE project_id = ?)', (id,))
    conn.execute('DELETE FROM functional_requirements WHERE project_id = ?', (id,))
    conn.execute('DELETE FROM personas WHERE project_id = ?', (id,))
    cur = conn.execute('DELETE FROM projects WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return cur.rowcount > 0
