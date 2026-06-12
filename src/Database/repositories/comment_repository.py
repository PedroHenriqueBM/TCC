from Database.database import get_connection
from datetime import datetime, timezone


def create_comment(id: str, entity_type: str, entity_id: str,
                   content: str, author: str) -> dict:
    conn = get_connection()
    now = datetime.now(timezone.utc).isoformat()
    conn.execute(
        'INSERT INTO comments (id, entity_type, entity_id, content, author, created_at) VALUES (?, ?, ?, ?, ?, ?)',
        (id, entity_type, entity_id, content, author, now)
    )
    conn.commit()
    conn.close()
    return {'id': id, 'entity_type': entity_type, 'entity_id': entity_id,
            'content': content, 'author': author, 'created_at': now}


def list_comments_by_entity(entity_type: str, entity_id: str) -> list[dict]:
    conn = get_connection()
    rows = conn.execute(
        'SELECT * FROM comments WHERE entity_type = ? AND entity_id = ? ORDER BY created_at ASC',
        (entity_type, entity_id)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def format_comments_as_text(comments: list[dict]) -> str:
    if not comments:
        return ""
    lines = []
    for c in comments:
        lines.append(f"[{c['created_at']}] {c['author']}: {c['content']}")
    return "\n".join(lines)
