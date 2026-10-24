---
data: 2026-10-23
status: provisório
camada: "sequenciador"
revoga:
revogada_por:
affects: []
evidence: [V-07, V-08, V-09]
---
# 031 – Sequenciador como nó único em Python

## Problema

Em que linguagem e em quantos processos o sequenciador roda? A escolha fixa a margem do RNF-03 (reação < T_seq = 100 ms), inclusive com a CPU do RPi saturada (V-08).

## Decisão

Um único nó ROS 2 em Python (rclpy), num único processo. Ele concentra a execução dos passos (ADR 032), a republicação do comando, a detecção de bordas, o heartbeat, o aviso de bateria e a consulta ao deliberador.

## Alternativa descartada

- **Nó único em C++:** latência menor e mais previsível, com cerca de 2 a 3 vezes mais código. A margem que ele ganha não é exigida pelo RNF-03.
- **Vários nós (sequenciador e monitores de heartbeat e bateria):** acrescenta um salto de tópico por evento e uma prioridade por processo. Os monitores só geram eventos para o mesmo sequenciador.

## Racional

- O RNF-03 pede um sequenciador rápido, sem garantia rígida. T_seq é cerca de 100 vezes a latência típica de um callback em rclpy, com ~140 mensagens/s de entrada.
- Gat: um sequenciador, um ponto de decisão. Heartbeat, bateria e falhas do controlador são eventos do mesmo sequenciador.
- Um processo só tem uma prioridade de tempo real para configurar e uma topologia mínima para inspecionar na V-09.

## Nota

- Se a V-07 ou a V-08 reprovar, a migração é para C++. A estrutura de passos e reações porta sem mudar.
- Nó único não impede módulos separados no código; a decisão é sobre processos.
