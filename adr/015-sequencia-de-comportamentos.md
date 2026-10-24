---
data: 2026-10-11
status: provisório
camada: "Sequenciador"
revoga:
revogada_por:
affects: []
evidence: []
---
# 015 - Sequência de comportamentos primitivos

## Problema

Qual lógica de comportamentos deve ser utilizada para guiar a trajetória do controle?

## Decisão

Sequência de comportamentos primitivos, definidos na ADR 024.

## Alternativa descartada

Usar o controller server do Nav2 para seguir o caminho.

## Racional

O controller server do Nav2 é um laço de realimentação que liga sensores (pose e costmap) a atuadores (cmd_vel), que na definição de Gat é um papel da camada do controlador.
