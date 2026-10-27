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

Estado seguro em reset: entradas do driver em nível baixo por pull-down, mais watchdog de hardware no ESP32-S3.
Na gravação pela USB nativa, os pinos mantêm o último estado (o reset que leva ao modo de gravação não reinicia os
periféricos): grava-se com a chave dos motores desligada (nota 0009).

## Alternativa descartada

Confiar apenas no firmware.

## Racional

Rodas não podem girar com o MCU em boot, travado ou sendo gravado.
