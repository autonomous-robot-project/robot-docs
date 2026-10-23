---
data: 2026-08-15
status: provisório
camada: "Controlador (medição) / Sequenciador (resposta)"
revoga:
revogada_por:
affects: []
evidence: []
---
# 009 - Medição de bateria

## Problema

Como devo medir o nível atual de bateria?

## Decisão

Divisor 47 kΩ / 10 kΩ com 100 nF no ADC1; publicação de BatteryState; limiares de bateria baixa e crítica.

## Alternativa descartada

Sensor de corrente INA219/INA226 com estimativa de carga.

## Racional

As duas decisões necessárias (avisar e parar/desligar) dependem apenas da tensão.
