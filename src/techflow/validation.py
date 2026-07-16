"""Input validation rules shared by create and update operations."""

from __future__ import annotations

from datetime import date


STATUSES = {"todo", "in_progress", "done"}


def validate_task(form: dict[str, str]) -> tuple[dict[str, str | None], list[str]]:
    """Normalize task form data and return human-readable validation errors."""
    title = form.get("title", "").strip()
    description = form.get("description", "").strip()
    status = form.get("status", "todo").strip()
    due_date = form.get("due_date", "").strip() or None
    errors: list[str] = []

    if not title:
        errors.append("Informe um título para a tarefa.")
    elif len(title) > 120:
        errors.append("O título deve ter no máximo 120 caracteres.")
    if len(description) > 1000:
        errors.append("A descrição deve ter no máximo 1000 caracteres.")
    if status not in STATUSES:
        errors.append("Selecione um status válido.")
    if due_date:
        try:
            date.fromisoformat(due_date)
        except ValueError:
            errors.append("Informe o prazo no formato AAAA-MM-DD.")

    return {
        "title": title,
        "description": description,
        "status": status,
        "due_date": due_date,
    }, errors
