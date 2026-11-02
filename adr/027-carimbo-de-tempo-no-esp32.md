---
data: 2026-10-23
status: provisório
camada: "controlador"
revoga:
revogada_por:
affects: []
evidence: [V-04, V-07, V-09]
---
# 027 – Carimbo de tempo no ESP32 com relógio sincronizado ao agente

## Problema

O TF casa cada varredura do LiDAR com a pose do mesmo instante pelo carimbo de tempo. O ESP32 e o RPi têm relógios independentes.

## Decisão

A tarefa de controle registra o instante de cada pose no relógio local do ESP32. A tarefa micro-ROS sincroniza periodicamente esse relógio com o do agente e converte o instante local para a base do RPi ao publicar.

A odometria só é publicada depois da primeira sincronização.

## Alternativa descartada

- **Carimbo na chegada, no RPi:** dispensa a sincronização, mas atrasa o carimbo pelo tempo do enlace, com jitter, e o atraso vira erro de ângulo no casamento durante os giros.

## Racional

- O instante da medida é um dado da medida. Quem mede é quem sabe quando mediu.
- A sincronização e a conversão ficam na tarefa micro-ROS, fora do laço de controle (RNF-01). O controlador continua sem depender do micro-ROS (ADR 018).
- É o padrão em sistemas com micro-ROS ou XRCE-DDS no MCU. A alternativa continua disponível por um parâmetro do `odom_to_tf_ros2` (ADR 026).

## Nota

O período de ressincronização será fixado pela deriva medida entre os relógios. A medida usa os carimbos da Odometria gravados na V-07, sem mudar o firmware. O enlace lê o relógio local antes do relógio do micro-ROS, e o que roda entre as duas leituras (preempção, interrupção) atrasa o carimbo, nunca o adianta (nota 0018). Por isso a fase de cada carimbo (a soma dos intervalos arredondados a T_c) é o offset mais esse atraso, e o mínimo dela em janelas de 1 s fica plano entre ressincronizações (±16 µs nos bags da nota 0018). Cada ressincronização dá um degrau igual à deriva acumulada no período mais a diferença de erro entre duas sincronizações. O offset de cada platô é a mediana dos mínimos das janelas. A deriva é a variação do offset entre o platô depois do primeiro degrau e o platô depois do último, dividida pelo tempo entre eles: o offset antes do primeiro degrau vem de uma ressincronização fora da gravação. O erro de sincronização é o espalhamento dos degraus.
