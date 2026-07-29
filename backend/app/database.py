import os
from contextlib import contextmanager
from pathlib import Path

import psycopg
from dotenv import load_dotenv
from psycopg.rows import dict_row


load_dotenv(Path(__file__).resolve().parent.parent / ".env", override=True)

class DatabaseNotConfigured(RuntimeError):
    pass


def _database_url() -> str:
    database_url = os.getenv("DATABASE_URL", "").strip()
    if not database_url or database_url.lower() in {"none", "null", "undefined"}:
        raise DatabaseNotConfigured("DATABASE_URL is required. Configure your Neon PostgreSQL connection string.")
    return database_url


@contextmanager
def get_db():
    connection = psycopg.connect(_database_url(), row_factory=dict_row)
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def row_to_dict(row):
    return dict(row) if row else None


def init_db():
    with get_db() as db:
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id BIGSERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('Citizen', 'Responder')),
                responder_type TEXT,
                location TEXT,
                availability_status TEXT,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
            """
        )
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS incidents (
                id BIGSERIAL PRIMARY KEY,
                citizen_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                description TEXT NOT NULL,
                location TEXT NOT NULL,
                latitude TEXT,
                longitude TEXT,
                people_affected TEXT,
                image_path TEXT,
                audio_path TEXT,
                incident_type TEXT NOT NULL DEFAULT 'Pending Analysis',
                incident_category TEXT NOT NULL DEFAULT 'General',
                severity TEXT NOT NULL DEFAULT 'Medium',
                confidence INTEGER NOT NULL DEFAULT 0,
                priority_reason TEXT NOT NULL DEFAULT '',
                ai_reason JSONB NOT NULL DEFAULT '[]'::jsonb,
                ai_summary TEXT NOT NULL DEFAULT '',
                impact_analysis TEXT NOT NULL DEFAULT '',
                safety_recommendations JSONB NOT NULL DEFAULT '[]'::jsonb,
                recommended_responder TEXT NOT NULL DEFAULT '',
                responder_reason TEXT NOT NULL DEFAULT '',
                emergency_contact JSONB NOT NULL DEFAULT '{}'::jsonb,
                public_advisory TEXT NOT NULL DEFAULT '',
                is_emergency BOOLEAN NOT NULL DEFAULT FALSE,
                status TEXT NOT NULL DEFAULT 'Reported',
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
            """
        )
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS responder_assignments (
                id BIGSERIAL PRIMARY KEY,
                incident_id BIGINT NOT NULL REFERENCES incidents(id) ON DELETE CASCADE,
                responder_id BIGINT REFERENCES users(id) ON DELETE SET NULL,
                recommended_responder TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Assigned',
                assigned_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
            """
        )
        db.execute("CREATE INDEX IF NOT EXISTS idx_incidents_citizen_id ON incidents(citizen_id)")
        db.execute("CREATE INDEX IF NOT EXISTS idx_incidents_responder ON incidents(recommended_responder)")
        db.execute("CREATE INDEX IF NOT EXISTS idx_incidents_emergency ON incidents(is_emergency)")
        db.execute("CREATE INDEX IF NOT EXISTS idx_assignments_responder ON responder_assignments(responder_id)")
        db.execute("CREATE INDEX IF NOT EXISTS idx_assignments_incident ON responder_assignments(incident_id)")
        db.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_assignments_unique_responder ON responder_assignments(incident_id, responder_id)")


def reset_database():
    with get_db() as db:
        db.execute("TRUNCATE TABLE responder_assignments, incidents, users RESTART IDENTITY CASCADE")
