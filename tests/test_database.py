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
            "description": "Priorizar o lote da manhã",
            "priority": "high",
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
        self.repository.create_task(self.task_data(priority="critical", status="todo"))
        self.repository.create_task(self.task_data(priority="low", status="done"))
        self.assertEqual(1, len(self.repository.list_tasks(priority="critical")))
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


if __name__ == "__main__":
    unittest.main()
