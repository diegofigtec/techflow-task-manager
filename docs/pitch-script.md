# Roteiro do vídeo pitch (até 4 minutos)

## 0:00-0:30 — Abertura

“Olá, eu sou [SEU NOME]. Este é o TechFlow Task Manager, desenvolvido para uma startup de
logística acompanhar tarefas, prioridades e prazos em tempo real. O projeto aplica conceitos de
Engenharia de Software desde a modelagem até a integração contínua.”

**Mostrar:** página inicial do repositório e README.

## 0:30-1:05 — Metodologia e Kanban

“Foi adotado um modelo híbrido de Scrum e Kanban. O backlog e os critérios de aceite orientam
pequenas entregas, enquanto o quadro To Do, In Progress e Done deixa o fluxo visível. O limite
de trabalho em progresso reduz tarefas iniciadas e não concluídas.”

**Mostrar:** GitHub Projects, destacando pelo menos dez cards.

## 1:05-2:05 — Sistema funcionando

“No painel é possível criar, consultar, editar, concluir e excluir tarefas. Cada tarefa possui
prioridade, status, descrição e prazo. Os indicadores resumem o trabalho da equipe e os filtros
ajudam o gestor a focar itens críticos.”

**Demonstrar:** criar uma tarefa crítica, editá-la, filtrá-la e marcá-la como concluída.

## 2:05-2:40 — Testes e qualidade

“A solução possui testes automatizados para regras de entrada, persistência SQLite e rotas HTTP.
O GitHub Actions valida a sintaxe, executa o Ruff e roda os testes nas versões 3.11 e 3.12 do
Python. Assim, regressões são detectadas antes de uma entrega.”

**Mostrar:** pasta `tests`, workflow e execução verde na aba Actions.

## 2:40-3:20 — Mudança de escopo

“Durante o desenvolvimento, o cliente solicitou controle de prazo e identificação de atrasos.
A mudança foi analisada, adicionada ao Kanban e implementada na versão 1.1. O banco recebeu o
campo de prazo, o painel passou a destacar atrasos e os testes foram atualizados.”

**Mostrar:** card da mudança, commit `feat: add due dates and overdue monitoring` e README.

## 3:20-3:50 — Reflexão final

“A Engenharia de Software transforma uma ideia em um produto verificável e sustentável. A
modelagem reduz ambiguidades, o versionamento preserva decisões, o método ágil melhora a
adaptação e os testes automatizados aumentam a confiança para evoluir o sistema.”

## 3:50-4:00 — Encerramento

“Obrigado. O código, a documentação, o histórico e as evidências estão disponíveis neste
repositório público.”

