---
data: 2026-10-25
status: provisório
camada: "controlador"
revoga:
revogada_por:
affects: []
evidence: []
---
# 044 – Alimentação do ESP32-S3 pela USB do RPi 5

## Problema

De onde o ESP32-S3 tira os 5 V no robô?

## Decisão

Da USB do RPi 5, ligada à USB nativa do devkit. A mesma porta serve para gravação e log (ADR 043).

## Alternativa descartada

- **5Vin por um buck a partir da bateria:** um conversor a mais, e o ESP32 passa a dividir o regulador com o ruído dos motores.
- **USB do CP2102:** ocuparia a porta da gravação. Com isso, gravar e ver o log exigiria trocar o cabo.

## Racional

- Com o RPi desligado, o ESP32 também desliga. Os drivers ficam em nível baixo (ADR 008), e as rodas não giram sem o sequenciador.
- O GND comum entre as camadas já vem pelo cabo. O fio de GND do enlace continua como referência junto ao TX/RX.
