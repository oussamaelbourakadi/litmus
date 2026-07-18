"""Alembic migration test: upgrade to head then downgrade to base.

Runs synchronously (no pytest-asyncio event loop) because Alembic's async env
drives its own event loop via ``asyncio.run``. The migration is exercised on a
temporary on-disk SQLite database using the same dialect-agnostic types as prod.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

from alembic.config import Config

from alembic import command

BACKEND_ROOT = Path(__file__).resolve().parents[1]


def _alembic_config(db_file: Path) -> Config:
    cfg = Config(str(BACKEND_ROOT / "alembic.ini"))
    cfg.set_main_option("script_location", str(BACKEND_ROOT / "alembic"))
    cfg.set_main_option("sqlalchemy.url", f"sqlite+aiosqlite:///{db_file}")
    return cfg


def test_upgrade_creates_projects_table(tmp_path: Path) -> None:
    db_file = tmp_path / "migration_test.db"
    cfg = _alembic_config(db_file)

    command.upgrade(cfg, "head")

    connection = sqlite3.connect(db_file)
    try:
        rows = connection.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    finally:
        connection.close()
    tables = {row[0] for row in rows}
    assert "projects" in tables


def test_downgrade_removes_projects_table(tmp_path: Path) -> None:
    db_file = tmp_path / "migration_downgrade.db"
    cfg = _alembic_config(db_file)

    command.upgrade(cfg, "head")
    command.downgrade(cfg, "base")

    connection = sqlite3.connect(db_file)
    try:
        rows = connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='projects'"
        ).fetchall()
    finally:
        connection.close()
    assert rows == []
