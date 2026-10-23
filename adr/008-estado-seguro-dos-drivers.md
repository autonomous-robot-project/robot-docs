---
data: 2026-08-15
status: provisório
camada: "Controlador"
revoga:
revogada_por:
affects: []
evidence: []
---
# 008 - Estado seguro dos drivers dos motores

## Problema

Como garantir start seguro dos drivers dos motores?

## Decisão

Estado seguro em reset e gravação: entradas do driver em nível baixo por pull-down, mais watchdog de hardware no ESP32-S3.

## Alternativa descartada

Confiar apenas no firmware.

## Racional

Rodas não podem girar com o MCU em boot, travado ou sendo gravado.
