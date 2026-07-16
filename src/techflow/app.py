"""WSGI application and HTTP routing for TechFlow Task Manager."""

from __future__ import annotations

import mimetypes
import os
from collections.abc import Callable, Iterable
from pathlib import Path
from urllib.parse import parse_qs

from .database import TaskRepository
from .validation import PRIORITIES, STATUSES, validate_task
from .views import dashboard, not_found, task_form

StartResponse = Callable[[str, list[tuple[str, str]]], None]


class TaskManagerApp:
    """Dependency-free WSGI application with explicit routes."""

    def __init__(self, database_path: str | Path | None = None) -> None:
        default_path = Path(__file__).resolve().parents[2] / "instance" / "techflow.db"
        self.repository = TaskRepository(
            database_path or os.getenv("TECHFLOW_DB", str(default_path))
        )
        self.static_dir = Path(__file__).resolve().parents[2] / "static"

    def __call__(
        self, environ: dict[str, object], start_response: StartResponse
    ) -> Iterable[bytes]:
        method = str(environ.get("REQUEST_METHOD", "GET")).upper()
        path = str(environ.get("PATH_INFO", "/"))

        if method == "GET" and path == "/":
            query = parse_qs(str(environ.get("QUERY_STRING", "")))
            status = query.get("status", [""])[0]
            priority = query.get("priority", [""])[0]
            overdue = query.get("overdue", [""])[0]
            status = status if status in STATUSES else ""
            priority = priority if priority in PRIORITIES else ""
            overdue = "1" if overdue == "1" else ""
            return self._html(
                start_response,
                dashboard(
                    self.repository.list_tasks(
                        status or None, priority or None, overdue_only=overdue == "1"
                    ),
                    self.repository.metrics(),
                    status,
                    priority,
                    overdue,
                ),
            )
        if method == "GET" and path == "/health":
            return self._response(start_response, "200 OK", b'{"status":"ok"}', "application/json")
        if method == "GET" and path == "/tasks/new":
            return self._html(start_response, task_form())
        if method == "POST" and path == "/tasks":
            return self._create(environ, start_response)
        if path.startswith("/static/") and method == "GET":
            return self._static(path, start_response)

        task_route = self._task_route(path)
        if task_route:
            task_id, action = task_route
            if method == "GET" and action == "edit":
                task = self.repository.get_task(task_id)
                return self._html(start_response, task_form(task)) if task else self._404(start_response)
            if method == "POST" and action == "edit":
                return self._update(task_id, environ, start_response)
            if method == "POST" and action == "delete":
                self.repository.delete_task(task_id)
                return self._redirect(start_response)
            if method == "POST" and action == "toggle":
                self.repository.toggle_task(task_id)
                return self._redirect(start_response)
        return self._404(start_response)

    @staticmethod
    def _task_route(path: str) -> tuple[int, str] | None:
        parts = path.strip("/").split("/")
        if len(parts) == 3 and parts[0] == "tasks" and parts[1].isdigit():
            return int(parts[1]), parts[2]
        return None

    @staticmethod
    def _read_form(environ: dict[str, object]) -> dict[str, str]:
        length = int(str(environ.get("CONTENT_LENGTH") or "0"))
        body = environ["wsgi.input"].read(length).decode("utf-8")  # type: ignore[union-attr]
        return {key: values[0] for key, values in parse_qs(body).items()}

    def _create(
        self, environ: dict[str, object], start_response: StartResponse
    ) -> Iterable[bytes]:
        data, errors = validate_task(self._read_form(environ))
        if errors:
            return self._html(start_response, task_form(data, errors), "422 Unprocessable Entity")
        self.repository.create_task(data)
        return self._redirect(start_response)

    def _update(
        self, task_id: int, environ: dict[str, object], start_response: StartResponse
    ) -> Iterable[bytes]:
        if not self.repository.get_task(task_id):
            return self._404(start_response)
        data, errors = validate_task(self._read_form(environ))
        data["id"] = str(task_id)
        if errors:
            return self._html(start_response, task_form(data, errors), "422 Unprocessable Entity")
        self.repository.update_task(task_id, data)
        return self._redirect(start_response)

    def _static(self, path: str, start_response: StartResponse) -> Iterable[bytes]:
        relative = path.removeprefix("/static/")
        candidate = (self.static_dir / relative).resolve()
        if self.static_dir.resolve() not in candidate.parents or not candidate.is_file():
            return self._404(start_response)
        content_type = mimetypes.guess_type(candidate.name)[0] or "application/octet-stream"
        return self._response(start_response, "200 OK", candidate.read_bytes(), content_type)

    @staticmethod
    def _response(
        start_response: StartResponse, status: str, body: bytes, content_type: str
    ) -> Iterable[bytes]:
        start_response(status, [("Content-Type", f"{content_type}; charset=utf-8"), ("Content-Length", str(len(body)))])
        return [body]

    def _html(
        self, start_response: StartResponse, body: str, status: str = "200 OK"
    ) -> Iterable[bytes]:
        return self._response(start_response, status, body.encode("utf-8"), "text/html")

    @staticmethod
    def _redirect(start_response: StartResponse) -> Iterable[bytes]:
        start_response("303 See Other", [("Location", "/"), ("Content-Length", "0")])
        return [b""]

    def _404(self, start_response: StartResponse) -> Iterable[bytes]:
        return self._html(start_response, not_found(), "404 Not Found")
