import sqlite3
import os
from pathlib import Path

DB_PATH = Path(os.path.dirname(os.path.abspath(__file__))) / '..' / 'Storage' / 'tcc.db'


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def initialize_database():
    conn = get_connection()
    c = conn.cursor()
    c.executescript('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            email TEXT NOT NULL UNIQUE,
            name TEXT,
            picture TEXT,
            google_token TEXT,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS projects (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'active',
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS personas (
            id TEXT PRIMARY KEY,
            project_id TEXT NOT NULL,
            name TEXT NOT NULL,
            opportunities TEXT,
            key_attributes TEXT,
            description TEXT,
            needs TEXT,
            challenges TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (project_id) REFERENCES projects(id)
        );

        CREATE TABLE IF NOT EXISTS functional_requirements (
            id TEXT PRIMARY KEY,
            project_id TEXT NOT NULL,
            name TEXT NOT NULL,
            url TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (project_id) REFERENCES projects(id)
        );

        CREATE TABLE IF NOT EXISTS requirement_personas (
            requirement_id TEXT NOT NULL,
            persona_id TEXT NOT NULL,
            PRIMARY KEY (requirement_id, persona_id),
            FOREIGN KEY (requirement_id) REFERENCES functional_requirements(id),
            FOREIGN KEY (persona_id) REFERENCES personas(id)
        );

        CREATE TABLE IF NOT EXISTS acceptance_criteria (
            id TEXT PRIMARY KEY,
            requirement_id TEXT NOT NULL,
            content TEXT NOT NULL,
            author TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (requirement_id) REFERENCES functional_requirements(id)
        );

        CREATE TABLE IF NOT EXISTS system_test_executions (
            id TEXT PRIMARY KEY,
            requirement_id TEXT NOT NULL,
            passed INTEGER NOT NULL,
            result_text TEXT,
            script_path TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (requirement_id) REFERENCES functional_requirements(id)
        );

        CREATE TABLE IF NOT EXISTS usability_inspection_executions (
            id TEXT PRIMARY KEY,
            requirement_id TEXT NOT NULL,
            result_text TEXT,
            recording_path TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (requirement_id) REFERENCES functional_requirements(id)
        );

        CREATE TABLE IF NOT EXISTS comments (
            id TEXT PRIMARY KEY,
            entity_type TEXT NOT NULL,
            entity_id TEXT NOT NULL,
            content TEXT NOT NULL,
            author TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
    ''')
    conn.commit()

    # Migration: add video_path column to system_test_executions if it doesn't exist yet
    try:
        conn.execute("ALTER TABLE system_test_executions ADD COLUMN video_path TEXT")
        conn.commit()
    except Exception:
        pass  # Column already exists

    conn.close()
