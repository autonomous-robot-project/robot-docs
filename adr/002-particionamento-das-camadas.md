---
data: 2026-08-15
status: definitivo
camada: "Controlador / Sequenciador / Deliberador"
revoga:
revogada_por:
affects: []
evidence: []
---
# 002 - Particionamento das camadas

## Problema

Como separar as camadas entre os sistemas?

## Decisão

Controlador no ESP32-S3; sequenciador e deliberador no RPi 5.

## Alternativa descartada

Todas as camadas no RPi 5.

## Racional

O controlador exige iteração de tempo limitado e constante (Gat); uma falha do Linux não pode interromper o laço de controle.
