---
data: 2026-10-24
status: provisório
camada: "sequenciador"
revoga:
revogada_por:
affects: []
evidence: [V-01, V-04, V-07, V-09]
---
# 032 – Sequenciador por passos e tabela de reações

## Problema

Como o sequenciador escolhe o próximo comportamento pelo resultado do atual (RF-04) e reage a eventos do controlador em menos de T_seq (RNF-03)? Os comportamentos primitivos são os da ADR 024; a ordem deles na trajetória, a da ADR 015.

## Decisão

Uma missão é uma lista de passos. Cada passo tem um comportamento, parâmetros calculados na entrada a partir da pose atual e um predicado de término.

- **Sucesso:** o predicado é satisfeito e o sequenciador avança para o próximo passo.
- **Falha:** uma borda de subida nas máscaras do Estado (ADR 025) consulta uma tabela de reações indexada pelo código. A reação é uma sub-lista de passos inserida antes do passo atual, o aborto da missão ou ignorar o código naquele passo (ADR 037).

Missões de ensaio e a missão gerada pelo plano são dados no mesmo formato, executados pelo mesmo motor.

## Alternativa descartada

- **Máquina de estados plana com tabela de transições:** cada missão vira estados e transições escritos à mão. Com a recuperação, a tabela cresce em produto e tende ao universal plan que Gat descarta.
- **Biblioteca de máquina de estados (YASMIN):** mesma estrutura, com dependência e código de terceiros na inspeção.
- **Behavior Tree (py_trees_ros):** reavaliação por tick periódico, que soma o período do tick à reação.
- **Corrotinas:** o estado fica na pilha, e cada espera precisa ser cancelável pelos eventos.

## Racional

- Gat: uma sequência linear de primitivas não é confiável, e o sequenciador responde condicionalmente à situação. Aqui, quem responde são o predicado e a tabela de reações. A estrutura de resultado nominal com falha tratada pela causa é a do ESL.
- RF-04: sucesso e falha são caminhos explícitos e separados.
- RNF-03: cada evento custa a verificação de um predicado e uma consulta à tabela, sem busca nem projeção temporal.
- Missão como dado: os passos e a tabela são inspecionáveis na V-09.

## Nota

- Missões são escritas em Python com um vocabulário fixo: `Mission(steps, reactions)`, `Step(behavior, until, reactions)`, os comportamentos da ADR 024 e alvos explícitos (`MapPoint`, reconvertido a cada entrada; `Offset`, resolvido uma vez e compartilhado entre passos). Um formato declarativo (YAML) exigiria o mesmo vocabulário e mais um interpretador.
- Bordas só disparam reações; términos testam condições atuais. A reação é escolhida do código mais específico ao mais geral (passo, depois missão), com o aborto como padrão.
- É um subconjunto do ESL e do RAP: um método por passo, sem decomposição hierárquica nem tarefas paralelas. Os monitores (heartbeat, bateria, enlace) só geram eventos para a tabela.
- O conteúdo da tabela de reações é a questão da escada de recuperação.
