"""HTML rendering helpers for the dependency-free web interface."""

from __future__ import annotations

from html import escape
from typing import Any


PRIORITY_LABELS = {
    "low": "Baixa",
    "medium": "Média",
    "high": "Alta",
    "critical": "Crítica",
}
STATUS_LABELS = {
    "todo": "A fazer",
    "in_progress": "Em progresso",
    "done": "Concluída",
}


def _layout(content: str, title: str = "Painel") -> str:
    return f"""<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="Gerenciador ágil de tarefas da TechFlow Solutions">
  <title>{escape(title)} | TechFlow</title>
  <link rel="stylesheet" href="/static/style.css">
</head>
<body>
  <header class="topbar">
    <a class="brand" href="/">
      <span class="brand-mark">TF</span>
      <span><strong>TechFlow</strong><small>Task Manager</small></span>
    </a>
    <a class="button button-primary" href="/tasks/new">+ Nova tarefa</a>
  </header>
  <main class="container">{content}</main>
  <footer>Projeto acadêmico de Engenharia de Software · TechFlow Solutions</footer>
</body>
</html>"""


def dashboard(
    tasks: list[dict[str, Any]],
    metrics: dict[str, int],
    selected_status: str = "",
    selected_priority: str = "",
    selected_overdue: str = "",
) -> str:
    metric_cards = "".join(
        f'<article class="metric"><span>{value}</span><small>{label}</small></article>'
        for label, value in (
            ("Total", metrics["total"]),
            ("A fazer", metrics["todo"]),
            ("Em progresso", metrics["in_progress"]),
            ("Concluídas", metrics["done"]),
            ("Atrasadas", metrics["overdue"]),
        )
    )
    status_options = _options(STATUS_LABELS, selected_status, "Todos os status")
    priority_options = _options(
        PRIORITY_LABELS, selected_priority, "Todas as prioridades"
    )
    overdue_options = _options(
        {"1": "Apenas atrasadas"}, selected_overdue, "Todos os prazos"
    )
    task_cards = "".join(_task_card(task) for task in tasks)
    if not task_cards:
        task_cards = """
        <section class="empty-state">
          <span>✓</span>
          <h2>Nenhuma tarefa encontrada</h2>
          <p>Crie uma tarefa ou ajuste os filtros para visualizar o trabalho da equipe.</p>
          <a class="button button-primary" href="/tasks/new">Criar primeira tarefa</a>
        </section>"""
    content = f"""
    <section class="hero">
      <div><span class="eyebrow">Visão da operação</span>
      <h1>Trabalho claro. Entregas no prazo.</h1>
      <p>Acompanhe prioridades, progresso e prazos da equipe de logística em tempo real.</p></div>
      <div class="pulse"><span></span>Sistema operacional</div>
    </section>
    <section class="metrics">{metric_cards}</section>
    <section class="workspace">
      <div class="section-heading"><div><span class="eyebrow">Backlog</span><h2>Tarefas da equipe</h2></div>
        <form class="filters" method="get" action="/">
          <label>Status<select name="status">{status_options}</select></label>
          <label>Prioridade<select name="priority">{priority_options}</select></label>
          <label>Prazo<select name="overdue">{overdue_options}</select></label>
          <button class="button" type="submit">Filtrar</button>
          <a class="button button-ghost" href="/">Limpar</a>
        </form>
      </div>
      <div class="task-grid">{task_cards}</div>
    </section>"""
    return _layout(content)


def _options(labels: dict[str, str], selected: str, default_label: str) -> str:
    parts = [f'<option value="">{default_label}</option>']
    for value, label in labels.items():
        selected_attribute = " selected" if value == selected else ""
        parts.append(
            f'<option value="{value}"{selected_attribute}>{escape(label)}</option>'
        )
    return "".join(parts)


def _task_card(task: dict[str, Any]) -> str:
    task_id = int(task["id"])
    overdue = bool(task.get("overdue"))
    due_date = task.get("due_date")
    due = escape(due_date) if due_date else "Sem prazo"
    if overdue:
        due = f"Atrasada · {due}"
    description = escape(task.get("description") or "Sem descrição")
    return f"""
    <article class="task-card priority-{task['priority']}">
      <div class="task-meta">
        <span class="badge priority">{PRIORITY_LABELS[task['priority']]}</span>
        <span class="badge status-{task['status']}">{STATUS_LABELS[task['status']]}</span>
      </div>
      <h3>{escape(task['title'])}</h3>
      <p>{description}</p>
      <div class="task-footer">
        <span class="due{' overdue' if overdue else ''}">◷ {due}</span>
        <div class="actions">
          <form method="post" action="/tasks/{task_id}/toggle">
            <button class="icon-button" title="Alternar conclusão">✓</button>
          </form>
          <a class="icon-button" title="Editar" href="/tasks/{task_id}/edit">✎</a>
          <form method="post" action="/tasks/{task_id}/delete" onsubmit="return confirm('Excluir esta tarefa?')">
            <button class="icon-button danger" title="Excluir">×</button>
          </form>
        </div>
      </div>
    </article>"""


def task_form(
    task: dict[str, Any] | None = None,
    errors: list[str] | None = None,
) -> str:
    task = task or {}
    is_edit = bool(task.get("id"))
    heading = "Editar tarefa" if is_edit else "Nova tarefa"
    action = f"/tasks/{task['id']}/edit" if is_edit else "/tasks"
    error_html = ""
    if errors:
        items = "".join(f"<li>{escape(error)}</li>" for error in errors)
        error_html = f'<div class="alert"><strong>Revise os dados:</strong><ul>{items}</ul></div>'
    priority_options = _options(
        PRIORITY_LABELS, str(task.get("priority", "medium")), "Prioridade"
    )
    status_options = _options(
        STATUS_LABELS, str(task.get("status", "todo")), "Status"
    )
    content = f"""
    <section class="form-shell">
      <a class="back-link" href="/">← Voltar ao painel</a>
      <div class="form-card">
        <span class="eyebrow">Planejamento ágil</span><h1>{heading}</h1>
        <p>Registre informações objetivas para que toda a equipe entenda a entrega.</p>
        {error_html}
        <form method="post" action="{action}" class="task-form">
          <label>Título <span>*</span>
            <input name="title" maxlength="120" required value="{escape(str(task.get('title', '')))}" placeholder="Ex.: Validar rota de entrega">
          </label>
          <label>Descrição
            <textarea name="description" maxlength="1000" rows="5" placeholder="Contexto e critérios de aceite">{escape(str(task.get('description', '')))}</textarea>
          </label>
          <div class="form-row">
            <label>Prioridade <span>*</span><select name="priority" required>{priority_options}</select></label>
            <label>Status <span>*</span><select name="status" required>{status_options}</select></label>
            <label>Prazo<input type="date" name="due_date" value="{escape(str(task.get('due_date') or ''))}"></label>
          </div>
          <div class="form-actions"><a class="button button-ghost" href="/">Cancelar</a>
            <button class="button button-primary" type="submit">Salvar tarefa</button></div>
        </form>
      </div>
    </section>"""
    return _layout(content, heading)


def not_found() -> str:
    return _layout(
        '<section class="empty-state"><span>404</span><h1>Página não encontrada</h1>'
        '<p>O endereço solicitado não existe.</p><a class="button" href="/">Voltar</a></section>',
        "Não encontrado",
    )
