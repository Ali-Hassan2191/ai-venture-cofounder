"""
SQLite Database initialization and connection management.
"""
import os
import sqlite3
from contextlib import contextmanager
from typing import Generator
from utils.constants import DEFAULT_DB_PATH


def get_db_path() -> str:
    """Returns absolute path to SQLite database."""
    os.makedirs(os.path.dirname(DEFAULT_DB_PATH), exist_ok=True)
    return DEFAULT_DB_PATH


@contextmanager
def get_db() -> Generator[sqlite3.Connection, None, None]:
    """Context manager for SQLite database connection with row factory."""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path, timeout=30.0, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        conn.execute("PRAGMA busy_timeout = 30000;")
        try:
            # Use DELETE journal mode for maximum compatibility across container mounts
            conn.execute("PRAGMA journal_mode = DELETE;")
        except Exception:
            pass
        conn.execute("PRAGMA foreign_keys = ON;")
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db() -> None:
    """Initializes all database tables idempotently."""
    with get_db() as conn:
        cursor = conn.cursor()

        # Startups table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS startups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                idea TEXT NOT NULL,
                country TEXT NOT NULL,
                target_market TEXT NOT NULL,
                target_customer TEXT NOT NULL,
                budget REAL NOT NULL DEFAULT 0.0,
                currency TEXT NOT NULL DEFAULT '$',
                founder_name TEXT NOT NULL DEFAULT 'Founder',
                founder_experience TEXT NOT NULL DEFAULT 'Beginner',
                additional_context TEXT DEFAULT '',
                status TEXT NOT NULL DEFAULT 'created',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # Agent Results table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agent_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                startup_id INTEGER NOT NULL,
                agent_key TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                raw_output TEXT DEFAULT '',
                structured_output TEXT DEFAULT '{}',
                tokens_used INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (startup_id) REFERENCES startups(id) ON DELETE CASCADE
            );
        """)

        # Startup Analysis & CEO Evaluation table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                startup_id INTEGER NOT NULL UNIQUE,
                overall_score INTEGER DEFAULT 0,
                category_scores TEXT DEFAULT '{}',
                difficulty_level TEXT DEFAULT 'MEDIUM',
                difficulty_reasoning TEXT DEFAULT '',
                executive_summary TEXT DEFAULT '',
                problem_statement TEXT DEFAULT '',
                solution_statement TEXT DEFAULT '',
                usp TEXT DEFAULT '',
                business_model TEXT DEFAULT '',
                revenue_model TEXT DEFAULT '',
                core_features TEXT DEFAULT '[]',
                technical_direction TEXT DEFAULT '',
                financial_overview TEXT DEFAULT '',
                risk_analysis TEXT DEFAULT '{}',
                key_advantages TEXT DEFAULT '[]',
                major_risks TEXT DEFAULT '[]',
                recommended_next_steps TEXT DEFAULT '[]',
                feasibility_verdict TEXT DEFAULT 'Good Potential',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (startup_id) REFERENCES startups(id) ON DELETE CASCADE
            );
        """)

        # Roadmaps table (Dynamic Duration)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS roadmaps (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                startup_id INTEGER NOT NULL UNIQUE,
                total_duration_days INTEGER NOT NULL,
                current_day INTEGER DEFAULT 1,
                current_phase TEXT DEFAULT 'Validation',
                progress_percent REAL DEFAULT 0.0,
                milestones TEXT DEFAULT '[]',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (startup_id) REFERENCES startups(id) ON DELETE CASCADE
            );
        """)

        # Roadmap Tasks table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS roadmap_tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                roadmap_id INTEGER NOT NULL,
                day_number INTEGER NOT NULL,
                phase TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT DEFAULT '',
                is_completed INTEGER DEFAULT 0,
                notes TEXT DEFAULT '',
                milestone_tag TEXT DEFAULT '',
                FOREIGN KEY (roadmap_id) REFERENCES roadmaps(id) ON DELETE CASCADE
            );
        """)

        # Chat Messages table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                startup_id INTEGER NOT NULL,
                sender TEXT NOT NULL,
                message TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (startup_id) REFERENCES startups(id) ON DELETE CASCADE
            );
        """)

        # Reports table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                startup_id INTEGER NOT NULL,
                file_path TEXT NOT NULL,
                report_title TEXT NOT NULL,
                generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (startup_id) REFERENCES startups(id) ON DELETE CASCADE
            );
        """)
