# TechFlow Task Manager

[![Integração contínua](https://github.com/diegofigtec/techflow-task-manager/actions/workflows/ci.yml/badge.svg)](https://github.com/diegofigtec/techflow-task-manager/actions/workflows/ci.yml)

Sistema web de gerenciamento de tarefas criado para a **TechFlow Solutions**, empresa fictícia
que atende uma startup de logística. A aplicação oferece visibilidade do fluxo de trabalho e
acompanhamento de desempenho sem depender de frameworks ou
serviços externos.

## Objetivo e escopo

O produto permite que membros da equipe e gestores:

- criem, consultem, editem e excluam tarefas;
- organizem tarefas por status (`A fazer`, `Em progresso` e `Concluída`);
- filtrem o backlog por status e prazo;
- filtrem rapidamente apenas tarefas atrasadas;
- acompanhem indicadores de volume e progresso;
- definam prazos e identifiquem tarefas atrasadas.

O escopo acadêmico prioriza um CRUD funcional, persistência local em SQLite, interface responsiva,
testes automatizados, documentação e integração contínua. Autenticação, múltiplas equipes e
notificações estão fora da versão atual.

## Metodologia ágil

Foi adotada uma abordagem híbrida **Scrum + Kanban**:

- o backlog reúne histórias com critérios de aceite;
- pequenas entregas incrementais simulam sprints;
- o GitHub Projects torna o fluxo visível em `To Do`, `In Progress` e `Done`;
- a limitação de trabalho em progresso favorece foco e conclusão;
- testes e definição de pronto sustentam a qualidade de cada incremento.

O backlog usado para montar o quadro está em [docs/kanban-cards.md](docs/kanban-cards.md).

## Executar o sistema

### Requisitos

- Python 3.11 ou superior;
- nenhum pacote externo é necessário para executar a aplicação.

### Passos

```bash
git clone https://github.com/diegofigtec/techflow-task-manager.git
cd techflow-task-manager
python run.py
```

Acesse `http://127.0.0.1:8000`. O banco é criado automaticamente em
`instance/techflow.db`. Para usar outro caminho:

```bash
python run.py --database caminho/alternativo.db --port 8080
```

## Executar os testes

No Linux ou macOS:

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

No PowerShell:

```powershell
$env:PYTHONPATH="src"; python -m unittest discover -s tests -v
```

Os testes cobrem validação de entrada, operações CRUD no repositório SQLite, filtros, métricas e
rotas HTTP. O pipeline em `.github/workflows/ci.yml` também compila o código, executa o Ruff e
repete a suíte no Python 3.11 e 3.12.

## Estrutura

```text
techflow-task-manager/
├── .github/workflows/ci.yml   # integração contínua
├── docs/                      # UML, backlog e roteiro do vídeo
├── src/techflow/              # aplicação, banco, validação e interface
├── static/style.css           # identidade visual responsiva
├── tests/                     # testes automatizados
├── pyproject.toml             # metadados e configuração do Ruff
└── run.py                     # ponto de entrada
```

## Arquitetura e modelagem

A solução separa quatro responsabilidades: `TaskManagerApp` trata HTTP e roteamento,
`TaskRepository` concentra persistência, `validation` aplica regras de entrada e `views` produz
HTML. O SQLite mantém os dados em arquivo local. Os diagramas de casos de uso e classes estão em
[docs/uml.md](docs/uml.md).

A modelagem é importante porque transforma necessidades do cliente em representações que podem
ser discutidas antes do código. Ela reduz ambiguidades, esclarece responsabilidades, apoia casos
de teste e torna mudanças mais previsíveis.

## Mudança de escopo planejada — níveis de prioridade

**Versão-base atual:** o CRUD funcional permite registrar título, descrição, status e prazo. A
funcionalidade de prioridade foi deliberadamente retirada desta branch para representar o produto
antes da solicitação adicional do cliente.

**Solicitação do cliente:** adicionar níveis de prioridade (`baixa`, `média`, `alta` e `crítica`)
para diferenciar demandas urgentes e permitir que o gestor filtre o backlog.

**Impacto previsto:** a mudança exigirá um novo campo no banco, validação dos valores permitidos,
controles nos formulários, identificação visual nos cards, filtro no painel e novos testes. A
implementação deve ocorrer em um commit próprio para permitir a comparação entre a versão-base e
o incremento de escopo.

## Questões norteadoras

### Causas de falha em projetos ágeis e mitigação pelo GitHub

Escopo pouco claro, comunicação fragmentada, prioridades conflitantes, excesso de trabalho em
progresso e ausência de critérios de qualidade são causas recorrentes. Issues e Projects tornam
responsáveis, estados e critérios visíveis; commits preservam o histórico; pull requests apoiam
revisão; e Actions aplica verificações iguais a cada mudança.

### Principais beneficiados

- **Equipe operacional:** registra e atualiza o trabalho diário.
- **Gestor de logística:** identifica gargalos, atrasos e acompanha o andamento das demandas.
- **Cliente:** acompanha previsibilidade e evolução do produto.
- **Equipe de desenvolvimento:** usa requisitos rastreáveis, testes e histórico para evoluir o
  sistema com segurança.

### Como a integração contínua aumenta a confiabilidade

O workflow executa automaticamente verificações reproduzíveis após pushes e pull requests. Erros
de sintaxe, problemas estáticos e regressões cobertas pelos testes impedem que uma alteração pareça
correta apenas no computador do autor. O CI não elimina defeitos, mas reduz o risco e acelera o
feedback.

### Desafios de mudanças em projetos ágeis

Mudanças podem afetar prazo, arquitetura, dados e critérios de aceite. O tratamento adotado foi:
registrar a justificativa, analisar impacto, criar um card independente, atualizar modelo e testes,
implementar um incremento pequeno e documentar a decisão. Esse ciclo preserva adaptabilidade sem
perder rastreabilidade.

### Aplicação prática das metodologias estudadas

O backlog priorizado representa o trabalho; o Kanban mostra o fluxo; commits semânticos registram
incrementos; critérios de aceite e testes compõem a definição de pronto; e a mudança de escopo
demonstra inspeção e adaptação. Assim, os conceitos deixam de ser apenas teóricos e aparecem no
ciclo de vida do produto.

## Exemplo existente no mercado

O **Trello** é um exemplo concreto de gestão visual por cartões e colunas. O TechFlow aplica a
mesma ideia de transparência do fluxo, mas integra o backlog ao código, ao histórico de mudanças e
à automação de qualidade oferecidos pelo GitHub.

## Licença

Distribuído sob a licença MIT. Consulte [LICENSE](LICENSE).
