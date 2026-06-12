from Database.database import get_connection
from datetime import datetime, timezone


def create_system_test_execution(id: str, requirement_id: str, passed: bool,
                                  result_text: str = '', script_path: str = '',
                                  video_path: str = '') -> dict:
    conn = get_connection()
    now = datetime.now(timezone.utc).isoformat()
    conn.execute(
        '''INSERT INTO system_test_executions
           (id, requirement_id, passed, result_text, script_path, video_path, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?)''',
        (id, requirement_id, 1 if passed else 0, result_text, script_path, video_path or '', now)
    )
    conn.commit()
    conn.close()
    return {
        'id': id, 'requirement_id': requirement_id, 'passed': passed,
        'result_text': result_text, 'script_path': script_path,
        'video_path': video_path or '', 'created_at': now
    }


def list_system_test_executions_by_requirement(requirement_id: str) -> list[dict]:
    conn = get_connection()
    rows = conn.execute(
        'SELECT * FROM system_test_executions WHERE requirement_id = ? ORDER BY created_at DESC',
        (requirement_id,)
    ).fetchall()
    conn.close()
    result = []
    for r in rows:
        d = dict(r)
        d['passed'] = bool(d['passed'])
        result.append(d)
    return result


def create_usability_inspection_execution(id: str, requirement_id: str,
                                           result_text: str = '', recording_path: str = '') -> dict:
    conn = get_connection()
    now = datetime.now(timezone.utc).isoformat()
    conn.execute(
        '''INSERT INTO usability_inspection_executions
           (id, requirement_id, result_text, recording_path, created_at)
           VALUES (?, ?, ?, ?, ?)''',
        (id, requirement_id, result_text, recording_path, now)
    )
    conn.commit()
    conn.close()
    return {
        'id': id, 'requirement_id': requirement_id,
        'result_text': result_text, 'recording_path': recording_path, 'created_at': now
    }


def list_usability_inspection_executions_by_requirement(requirement_id: str) -> list[dict]:
    conn = get_connection()
    rows = conn.execute(
        'SELECT * FROM usability_inspection_executions WHERE requirement_id = ? ORDER BY created_at DESC',
        (requirement_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
