"""SQLite persistence for task records."""

from __future__ import annotations

import sqlite3
from contextlib import closing
from pathlib import Path
from typing import Any


SCHEMA = """
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL CHECK(length(title) BETWEEN 1 AND 120),
    description TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL DEFAULT 'todo'
        CHECK(status IN ('todo', 'in_progress', 'done')),
    due_date TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""


class TaskRepository:
    """Provide a small, explicit data-access layer around SQLite."""

    def __init__(self, database_path: str | Path) -> None:
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self.initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path, isolation_level=None)
        connection.row_factory = sqlite3.Row
        return connection

    def initialize(self) -> None:
        """Create the database schema when it does not exist."""
        with closing(self._connect()) as connection:
            connection.executescript(SCHEMA)

    def list_tasks(
        self,
        status: str | None = None,
        overdue_only: bool = False,
    ) -> list[dict[str, Any]]:
        clauses: list[str] = []
        parameters: list[str] = []
        if status:
            clauses.append("status = ?")
            parameters.append(status)
        if overdue_only:
            clauses.append(
                "due_date IS NOT NULL AND due_date < date('now') AND status != 'done'"
            )
        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        query = f"""
            SELECT *,
                   CASE
                     WHEN due_date IS NOT NULL
                      AND due_date < date('now')
                      AND status != 'done' THEN 1
                     ELSE 0
                   END AS overdue
            FROM tasks
            {where}
            ORDER BY
                due_date IS NULL,
                due_date,
                id DESC
        """
        with closing(self._connect()) as connection:
            return [dict(row) for row in connection.execute(query, parameters)]

    def get_task(self, task_id: int) -> dict[str, Any] | None:
        with closing(self._connect()) as connection:
            row = connection.execute(
                "SELECT * FROM tasks WHERE id = ?", (task_id,)
            ).fetchone()
        return dict(row) if row else None

    def create_task(self, data: dict[str, str | None]) -> int:
        with closing(self._connect()) as connection:
            cursor = connection.execute(
                """
                INSERT INTO tasks (title, description, status, due_date)
                VALUES (?, ?, ?, ?)
                """,
                (
                    data["title"],
                    data["description"],
                    data["status"],
                    data["due_date"],
                ),
            )
            return int(cursor.lastrowid)

    def update_task(self, task_id: int, data: dict[str, str | None]) -> bool:
        with closing(self._connect()) as connection:
            cursor = connection.execute(
                """
                UPDATE tasks
                   SET title = ?, description = ?, status = ?,
                       due_date = ?, updated_at = CURRENT_TIMESTAMP
                 WHERE id = ?
                """,
                (
                    data["title"],
                    data["description"],
                    data["status"],
                    data["due_date"],
                    task_id,
                ),
            )
            return cursor.rowcount > 0

    def toggle_task(self, task_id: int) -> bool:
        with closing(self._connect()) as connection:
            cursor = connection.execute(
                """
                UPDATE tasks
                   SET status = CASE WHEN status = 'done' THEN 'todo' ELSE 'done' END,
                       updated_at = CURRENT_TIMESTAMP
                 WHERE id = ?
                """,
                (task_id,),
            )
            return cursor.rowcount > 0

    def delete_task(self, task_id: int) -> bool:
        with closing(self._connect()) as connection:
            cursor = connection.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            return cursor.rowcount > 0

    def metrics(self) -> dict[str, int]:
        with closing(self._connect()) as connection:
            row = connection.execute(
                """
                SELECT COUNT(*) AS total,
                       SUM(status = 'todo') AS todo,
                       SUM(status = 'in_progress') AS in_progress,
                       SUM(status = 'done') AS done,
                       SUM(
                         due_date IS NOT NULL
                         AND due_date < date('now')
                         AND status != 'done'
                       ) AS overdue
                  FROM tasks
                """
            ).fetchone()
        return {key: int(row[key] or 0) for key in row.keys()}
