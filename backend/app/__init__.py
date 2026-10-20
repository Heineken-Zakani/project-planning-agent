import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "project_planning.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS projects (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            start_date TEXT NOT NULL,
            project_type TEXT,
            working_days TEXT DEFAULT '1,2,3,4,5',
            weekends TEXT DEFAULT '6,0',
            holidays TEXT DEFAULT '',
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS wbs (
            id TEXT PRIMARY KEY,
            project_id TEXT NOT NULL,
            parent_id TEXT,
            code TEXT NOT NULL,
            name TEXT NOT NULL,
            level INTEGER NOT NULL,
            template_name TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY(project_id) REFERENCES projects(id)
        );

        CREATE TABLE IF NOT EXISTS activities (
            id TEXT PRIMARY KEY,
            project_id TEXT NOT NULL,
            wbs_id TEXT,
            code TEXT NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            duration_days INTEGER NOT NULL,
            planned_start TEXT,
            planned_finish TEXT,
            actual_start TEXT,
            actual_finish TEXT,
            percent_complete REAL DEFAULT 0,
            status TEXT DEFAULT 'not_started',
            created_at TEXT NOT NULL,
            FOREIGN KEY(project_id) REFERENCES projects(id),
            FOREIGN KEY(wbs_id) REFERENCES wbs(id)
        );

        CREATE TABLE IF NOT EXISTS dependencies (
            id TEXT PRIMARY KEY,
            project_id TEXT NOT NULL,
            predecessor_id TEXT NOT NULL,
            successor_id TEXT NOT NULL,
            dependency_type TEXT NOT NULL DEFAULT 'FS',
            lag_days INTEGER DEFAULT 0,
            created_at TEXT NOT NULL,
            FOREIGN KEY(project_id) REFERENCES projects(id),
            FOREIGN KEY(predecessor_id) REFERENCES activities(id),
            FOREIGN KEY(successor_id) REFERENCES activities(id)
        );

        CREATE TABLE IF NOT EXISTS baselines (
            id TEXT PRIMARY KEY,
            project_id TEXT NOT NULL,
            name TEXT NOT NULL,
            snapshot TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(project_id) REFERENCES projects(id)
        );
        """
    )
    conn.commit()
    conn.close()


# Ensure initialization happens when module is imported.
init_db()
