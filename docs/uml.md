# Modelagem UML

Os diagramas abaixo registram a visão funcional e estrutural do TechFlow Task Manager.

## Diagrama de casos de uso

```mermaid
flowchart LR
    actor((Membro da equipe))
    gestor((Gestor do projeto))
    actor --> UC1[Criar tarefa]
    actor --> UC2[Consultar tarefas]
    actor --> UC3[Atualizar tarefa]
    actor --> UC4[Concluir tarefa]
    actor --> UC5[Excluir tarefa]
    gestor --> UC2
    gestor --> UC6[Filtrar por status e prioridade]
    gestor --> UC7[Monitorar indicadores e atrasos]
    UC7 -. inclui .-> UC2
```

## Diagrama de classes

```mermaid
classDiagram
    class TaskManagerApp {
        -TaskRepository repository
        +__call__(environ, start_response)
        -_create(environ, start_response)
        -_update(task_id, environ, start_response)
        -_static(path, start_response)
    }
    class TaskRepository {
        -Path database_path
        +initialize()
        +list_tasks(status, priority) list
        +get_task(task_id) dict
        +create_task(data) int
        +update_task(task_id, data) bool
        +toggle_task(task_id) bool
        +delete_task(task_id) bool
        +metrics() dict
    }
    class Task {
        +int id
        +str title
        +str description
        +str priority
        +str status
        +date due_date
        +datetime created_at
        +datetime updated_at
    }
    class Validation {
        +validate_task(form) tuple
    }
    class Views {
        +dashboard(tasks, metrics, filters) str
        +task_form(task, errors) str
        +not_found() str
    }
    TaskManagerApp --> TaskRepository : usa
    TaskRepository --> Task : persiste
    TaskManagerApp --> Validation : valida entrada
    TaskManagerApp --> Views : renderiza
```

## Por que modelar

A modelagem reduz ambiguidades antes da codificação. O diagrama de casos de uso aproxima o
sistema das necessidades dos usuários, enquanto o diagrama de classes explicita
responsabilidades, dependências e dados persistidos. Essa visão facilita estimativas, revisão,
testes e futuras mudanças sem exigir a leitura imediata de todo o código.

