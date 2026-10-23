---
data: 2026-10-11
status: provisório
camada: "Sequenciador / Deliberador"
revoga:
revogada_por:
affects: []
evidence: []
---
# 014 - Deliberador por consulta

## Problema

O sequenciador pede o plano ou o deliberador entrega uma missão com plano?

## Decisão

Os dois modelos existem em Gat, este trabalho vai dar preferência para consulta do sequenciador.

## Alternativa descartada

Produzir planos para o sequenciador executar. É o modelo do 3T.

## Racional

O planner server do Nav2 já funciona como consulta: recebe início e objetivo, devolve um caminho. Não é preciso nenhum nó extra com estado de missão.
