import io
import sys
import tempfile
import unittest
from pathlib import Path
from urllib.parse import urlencode

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from techflow.app import TaskManagerApp  # noqa: E402


class WSGITestClient:
    def __init__(self, app: TaskManagerApp) -> None:
        self.app = app

    def request(
        self, path: str, method: str = "GET", form: dict[str, str] | None = None
    ) -> tuple[str, dict[str, str], bytes]:
        body = urlencode(form or {}).encode("utf-8")
        environ: dict[str, object] = {
            "REQUEST_METHOD": method,
            "PATH_INFO": path.split("?", 1)[0],
            "QUERY_STRING": path.split("?", 1)[1] if "?" in path else "",
            "CONTENT_LENGTH": str(len(body)),
            "CONTENT_TYPE": "application/x-www-form-urlencoded",
            "wsgi.input": io.BytesIO(body),
        }
        response: dict[str, object] = {}

        def start_response(status: str, headers: list[tuple[str, str]]) -> None:
            response["status"] = status
            response["headers"] = dict(headers)

        content = b"".join(self.app(environ, start_response))
        return str(response["status"]), response["headers"], content


class TaskManagerAppTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        app = TaskManagerApp(Path(self.temporary_directory.name) / "web.db")
        self.client = WSGITestClient(app)

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def test_health_endpoint(self) -> None:
        status, _, body = self.client.request("/health")
        self.assertEqual("200 OK", status)
        self.assertEqual(b'{"status":"ok"}', body)

    def test_dashboard_is_rendered(self) -> None:
        status, _, body = self.client.request("/")
        self.assertEqual("200 OK", status)
        self.assertIn("TechFlow", body.decode("utf-8"))

    def test_overdue_filter_is_available(self) -> None:
        status, _, body = self.client.request("/?overdue=1")
        self.assertEqual("200 OK", status)
        self.assertIn("Apenas atrasadas", body.decode("utf-8"))

    def test_create_edit_toggle_and_delete_through_http(self) -> None:
        form = {
            "title": "Monitorar coleta",
            "description": "Acompanhar saída do veículo",
            "status": "todo",
            "due_date": "2030-06-01",
        }
        status, headers, _ = self.client.request("/tasks", "POST", form)
        self.assertEqual("303 See Other", status)
        self.assertEqual("/", headers["Location"])
        _, _, dashboard = self.client.request("/")
        self.assertIn("Monitorar coleta", dashboard.decode("utf-8"))

        form["title"] = "Monitorar coleta expressa"
        status, _, _ = self.client.request("/tasks/1/edit", "POST", form)
        self.assertEqual("303 See Other", status)
        status, _, _ = self.client.request("/tasks/1/toggle", "POST")
        self.assertEqual("303 See Other", status)
        status, _, _ = self.client.request("/tasks/1/delete", "POST")
        self.assertEqual("303 See Other", status)

    def test_invalid_form_returns_422(self) -> None:
        status, _, body = self.client.request("/tasks", "POST", {"title": ""})
        self.assertEqual("422 Unprocessable Entity", status)
        self.assertIn("Informe um título", body.decode("utf-8"))

    def test_unknown_route_returns_404(self) -> None:
        status, _, _ = self.client.request("/missing")
        self.assertEqual("404 Not Found", status)


if __name__ == "__main__":
    unittest.main()
