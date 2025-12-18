"""Database helpers using SQLAlchemy.

Provides: `get_engine`, `create_database_if_missing`, `run_schema`,
and `insert_artifact_data` as safe placeholders so the app's imports
resolve and local development can proceed.

This implementation uses the `mysql+mysqlconnector` driver. Ensure
`mysql-connector-python` and `SQLAlchemy` are installed in your venv.
"""
from typing import Any, List, Dict
import json
from sqlalchemy import create_engine, text


def get_engine(user: str, password: str, host: str, port: int, db_name: str):
    """Return a SQLAlchemy Engine connected to the specified database.

    Uses the `mysql+mysqlconnector` driver.
    """
    url = f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{db_name}"
    engine = create_engine(url, pool_pre_ping=True, future=True)
    return engine


def create_database_if_missing(user: str, password: str, host: str, port: int, db_name: str):
    """Create the database on the server if it does not exist.

    Connects to the server without selecting a database and issues
    `CREATE DATABASE IF NOT EXISTS`.
    """
    admin_url = f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/"
    admin_engine = create_engine(admin_url, pool_pre_ping=True, future=True)
    create_sql = f"CREATE DATABASE IF NOT EXISTS `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
    with admin_engine.begin() as conn:
        conn.execute(text(create_sql))


def run_schema(engine):
    """Create minimal tables required by the app if they don't exist.

    This creates three simple tables: `artifacts_meta`, `media`, and
    `colors`. The `data` columns are stored as JSON (MySQL JSON type).
    """
    create_artifacts = (
        """
        CREATE TABLE IF NOT EXISTS artifacts_meta (
            id INT AUTO_INCREMENT PRIMARY KEY,
            object_number VARCHAR(255),
            classification VARCHAR(255),
            data JSON
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """
    )

    create_media = (
        """
        CREATE TABLE IF NOT EXISTS media (
            id INT AUTO_INCREMENT PRIMARY KEY,
            artifact_object_number VARCHAR(255),
            data JSON
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """
    )

    create_colors = (
        """
        CREATE TABLE IF NOT EXISTS colors (
            id INT AUTO_INCREMENT PRIMARY KEY,
            artifact_object_number VARCHAR(255),
            data JSON
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """
    )

    with engine.begin() as conn:
        conn.execute(text(create_artifacts))
        conn.execute(text(create_media))
        conn.execute(text(create_colors))


def insert_artifact_data(engine, meta: List[Dict[str, Any]], media: List[Dict[str, Any]], colors: List[Dict[str, Any]]):
    """Insert lists of meta/media/colors into their respective tables.

    This function is intentionally conservative: it attempts to extract
    an `objectnumber` (or `object_number`) from meta items to relate
    records; otherwise it inserts the JSON payload as-is.
    """
    insert_meta_sql = text(
        "INSERT INTO artifacts_meta (object_number, classification, data) VALUES (:object_number, :classification, :data)"
    )
    insert_media_sql = text(
        "INSERT INTO media (artifact_object_number, data) VALUES (:artifact_object_number, :data)"
    )
    insert_colors_sql = text(
        "INSERT INTO colors (artifact_object_number, data) VALUES (:artifact_object_number, :data)"
    )

    with engine.begin() as conn:
        for item in meta:
            obj_num = item.get("objectnumber") or item.get("object_number") or item.get("id")
            classification = item.get("classification") or None
            conn.execute(insert_meta_sql, {
                "object_number": str(obj_num) if obj_num is not None else None,
                "classification": classification,
                "data": json.dumps(item, default=str),
            })

        for m in media:
            artifact_ref = m.get("objectnumber") or m.get("object_number") or m.get("id")
            conn.execute(insert_media_sql, {
                "artifact_object_number": str(artifact_ref) if artifact_ref is not None else None,
                "data": json.dumps(m, default=str),
            })

        for c in colors:
            artifact_ref = c.get("objectnumber") or c.get("object_number") or c.get("id")
            conn.execute(insert_colors_sql, {
                "artifact_object_number": str(artifact_ref) if artifact_ref is not None else None,
                "data": json.dumps(c, default=str),
            })
