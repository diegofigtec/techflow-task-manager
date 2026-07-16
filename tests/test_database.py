import sqlite3
import tempfile
import unittest
from pathlib import Path

from techflow.database import TaskRepository


class TaskRepositoryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.repository = TaskRepository(
            Path(self.temporary_directory.name) / "test.db"
        )

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    @staticmethod
    def task_data(**overrides: str | None) -> dict[str, str | None]:
        data: dict[str, str | None] = {
            "title": "Separar pedidos",
            "description": "Conferir o lote da manhã",
            "status": "todo",
            "due_date": "2030-01-10",
        }
        data.update(overrides)
        return data

    def test_crud_lifecycle(self) -> None:
        task_id = self.repository.create_task(self.task_data())
        created = self.repository.get_task(task_id)
        self.assertIsNotNone(created)
        self.assertEqual("Separar pedidos", created["title"])

        updated = self.repository.update_task(
            task_id, self.task_data(title="Separar e conferir pedidos", status="in_progress")
        )
        self.assertTrue(updated)
        self.assertEqual("in_progress", self.repository.get_task(task_id)["status"])

        self.assertTrue(self.repository.toggle_task(task_id))
        self.assertEqual("done", self.repository.get_task(task_id)["status"])
        self.assertTrue(self.repository.delete_task(task_id))
        self.assertIsNone(self.repository.get_task(task_id))

    def test_filters_and_metrics(self) -> None:
        self.repository.create_task(self.task_data(status="todo"))
        self.repository.create_task(self.task_data(status="done"))
        self.assertEqual(1, len(self.repository.list_tasks(status="done")))
        self.assertEqual(
            {"total": 2, "todo": 1, "in_progress": 0, "done": 1, "overdue": 0},
            self.repository.metrics(),
        )

    def test_filters_only_overdue_open_tasks(self) -> None:
        self.repository.create_task(
            self.task_data(title="Atrasada", due_date="2020-01-01", status="todo")
        )
        self.repository.create_task(
            self.task_data(title="Concluída", due_date="2020-01-01", status="done")
        )
        overdue = self.repository.list_tasks(overdue_only=True)
        self.assertEqual(["Atrasada"], [task["title"] for task in overdue])

    def test_new_schema_has_no_priority_column(self) -> None:
        connection = sqlite3.connect(self.repository.database_path)
        try:
            columns = [row[1] for row in connection.execute("PRAGMA table_info(tasks)")]
        finally:
            connection.close()
        self.assertNotIn("priority", columns)

    def test_remains_compatible_with_legacy_priority_database(self) -> None:
        legacy_path = Path(self.temporary_directory.name) / "legacy.db"
        connection = sqlite3.connect(legacy_path)
        try:
            connection.execute(
                """
                CREATE TABLE tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL DEFAULT '',
                    priority TEXT NOT NULL DEFAULT 'medium',
                    status TEXT NOT NULL DEFAULT 'todo',
                    due_date TEXT,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            connection.commit()
        finally:
            connection.close()
        legacy_repository = TaskRepository(legacy_path)
        task_id = legacy_repository.create_task(self.task_data())
        self.assertEqual("medium", legacy_repository.get_task(task_id)["priority"])


if __name__ == "__main__":
    unittest.main()
