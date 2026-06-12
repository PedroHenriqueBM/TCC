from Database.database import get_connection
from datetime import datetime, timezone


def create_functional_requirement(id: str, project_id: str, name: str, url: str = '') -> dict:
    conn = get_connection()
    now = datetime.now(timezone.utc).isoformat()
    conn.execute(
        'INSERT INTO functional_requirements (id, project_id, name, url, created_at) VALUES (?, ?, ?, ?, ?)',
        (id, project_id, name, url, now)
    )
    conn.commit()
    conn.close()
    return {'id': id, 'project_id': project_id, 'name': name, 'url': url, 'created_at': now}


def get_functional_requirement_by_id(id: str) -> dict | None:
    conn = get_connection()
    row = conn.execute('SELECT * FROM functional_requirements WHERE id = ?', (id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def list_functional_requirements_by_project(project_id: str) -> list[dict]:
    conn = get_connection()
    rows = conn.execute(
        'SELECT * FROM functional_requirements WHERE project_id = ? ORDER BY created_at DESC',
        (project_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def functional_requirement_exists(id: str) -> bool:
    conn = get_connection()
    row = conn.execute('SELECT 1 FROM functional_requirements WHERE id = ?', (id,)).fetchone()
    conn.close()
    return row is not None


def link_persona_to_requirement(requirement_id: str, persona_id: str):
    conn = get_connection()
    conn.execute(
        'INSERT OR IGNORE INTO requirement_personas (requirement_id, persona_id) VALUES (?, ?)',
        (requirement_id, persona_id)
    )
    conn.commit()
    conn.close()


def update_functional_requirement(id: str, name: str, url: str = '',
                                   persona_ids: list[str] = None) -> bool:
    conn = get_connection()
    cur = conn.execute(
        'UPDATE functional_requirements SET name = ?, url = ? WHERE id = ?',
        (name, url, id)
    )
    if persona_ids is not None:
        conn.execute('DELETE FROM requirement_personas WHERE requirement_id = ?', (id,))
        for pid in persona_ids:
            conn.execute(
                'INSERT OR IGNORE INTO requirement_personas (requirement_id, persona_id) VALUES (?, ?)',
                (id, pid)
            )
    conn.commit()
    conn.close()
    return cur.rowcount > 0


def delete_functional_requirement(id: str) -> bool:
    conn = get_connection()
    conn.execute('DELETE FROM requirement_personas WHERE requirement_id = ?', (id,))
    conn.execute('DELETE FROM acceptance_criteria WHERE requirement_id = ?', (id,))
    conn.execute('DELETE FROM usability_inspection_executions WHERE requirement_id = ?', (id,))
    conn.execute('DELETE FROM system_test_executions WHERE requirement_id = ?', (id,))
    conn.execute('DELETE FROM comments WHERE entity_id = ?', (id,))
    cur = conn.execute('DELETE FROM functional_requirements WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return cur.rowcount > 0


def get_personas_of_requirement(requirement_id: str) -> list[dict]:
    conn = get_connection()
    rows = conn.execute(
        '''SELECT p.* FROM personas p
           INNER JOIN requirement_personas rp ON rp.persona_id = p.id
           WHERE rp.requirement_id = ?''',
        (requirement_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
