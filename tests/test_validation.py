import unittest

from techflow.validation import validate_task


class TaskValidationTests(unittest.TestCase):
    def test_accepts_valid_task(self) -> None:
        data, errors = validate_task(
            {
                "title": "  Conferir expedição  ",
                "description": "Validar o lote",
                "priority": "critical",
                "status": "in_progress",
                "due_date": "2030-05-20",
            }
        )
        self.assertEqual([], errors)
        self.assertEqual("Conferir expedição", data["title"])
        self.assertEqual("2030-05-20", data["due_date"])

    def test_rejects_missing_title(self) -> None:
        _, errors = validate_task({"title": ""})
        self.assertIn("Informe um título para a tarefa.", errors)

    def test_rejects_invalid_enumerations_and_date(self) -> None:
        _, errors = validate_task(
            {
                "title": "Tarefa",
                "priority": "urgent",
                "status": "blocked",
                "due_date": "31/12/2030",
            }
        )
        self.assertEqual(3, len(errors))


if __name__ == "__main__":
    unittest.main()

