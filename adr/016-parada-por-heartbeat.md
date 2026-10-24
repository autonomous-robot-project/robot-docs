---
data: 2026-10-11
status: definitivo
camada: "Sequenciador"
revoga: "004 (planilha)"
revogada_por:
affects: []
evidence: []
---
# 016 - Parada remota por heartbeat com o notebook

## Problema

Como parar o robô em movimento?

## Decisão

Heartbeat com notebook.

## Alternativa descartada

Parada remota pelo M5StickC Plus2 via ESP-NOW com heartbeat; perda de pacotes acima do timeout zera os motores.

## Racional

A alternativa exigiria:
- mais um dispositivo, com firmware próprio;
- o rádio Wi-Fi do ESP32-S3 ligado para o ESP-NOW, com interrupções de rádio no núcleo 0;
- mais uma tarefa e um protocolo para manter;
- um caminho a mais até o atuador, que entraria na inspeção de código e na análise de tempo.
