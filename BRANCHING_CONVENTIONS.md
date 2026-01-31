# Branching Conventions

Este repositório utiliza um fluxo baseado em branches temporárias com squash merges para manter o histórico da branch `main` limpo e representativo dos ciclos de trabalho.

## Tipos de Branches Temporárias

- `task/NOME_DA_TAREFA`  
  Para execução de tarefas práticas, testes e logs de progresso relacionados a uma atividade específica.
  
- `doc/NOME_DO_SISTEMA`  
  Para criação ou revisão de documentação técnica sobre um sistema específico do robô.

- `dev-log/TEMA_DA_REFLEXAO`  
  Para anotações reflexivas ou registros que não estão vinculados diretamente a uma tarefa ou sistema.

## Convenções Gerais

- Cada branch representa um **ciclo de trabalho coeso** com objetivo definido.
- Um ciclo pode conter múltiplos commits de diferentes tipos (`log`, `reflect`, `write`...), desde que relacionados ao mesmo sistema ou escopo.
- **Evite misturar** documentação técnica com logs de tarefa na mesma branch.
- Utilize `squash merge` ao integrar à `main`, com uma **mensagem de resumo descritiva e clara**.

## Exemplo

```bash
git checkout -b task/controle-pid-v1
# (fazer commits)
git commit -m "log: primeiro teste com kp = 0.8"
git commit -m "reflect: impacto da kd na estabilidade"
# merge com squash:
git checkout main
git merge --squash task/controle-pid-v1
git commit -m "task: controle pid v1 — ajustes e observações"
