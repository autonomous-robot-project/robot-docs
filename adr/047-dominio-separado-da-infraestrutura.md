---
data: 2026-10-27
status: provisório
camada: "controlador / sequenciador / deliberador"
revoga:
revogada_por:
affects: [robot-firmware/components, robot-ros-system]
evidence: [V-02, V-06]
---
# 047 - Domínio separado da infraestrutura em todas as camadas

## Problema

Os requisitos de cada camada viram código em duas partes: o domínio (controle, supervisão, vencimento, passos e
reações do sequenciador, tratamento do plano, medidas e critérios das verificações) e a infraestrutura (periféricos,
FreeRTOS, relógio, micro-ROS, rclpy, leitura de bags). Juntas na mesma classe, o domínio só pode ser exercitado no
sistema montado, e um erro numa medida da verificação fica indistinguível de um erro no que ela mede.

## Decisão

Em todo código próprio das três camadas, o domínio fica em classes puras, sem dependência da plataforma, que recebem
leituras e instantes como parâmetro:

- **controlador:** sem ESP-IDF nem FreeRTOS. O `controller.cpp` orquestra o ciclo: lê o relógio e os sensores, chama o
  domínio e aplica o resultado. Os medidores das verificações ficam em `instrumentation/`.
- **sequenciador e deliberador:** sem rclpy. O nó só traduz mensagens, timers e actions em chamadas ao domínio. O
  planejamento em si é do Nav2 (ADR 034), que é infraestrutura de terceiros.
- **verificações:** o critério não depende do ROS, que só lê o bag.

## Alternativa descartada

- **Domínio dentro das classes de plataforma** (periférico, nó ROS): só verificável no sistema montado.
- **Camada de abstração da plataforma com interfaces:** indireção em todo acesso, sem requisito que a peça.

## Racional

- O domínio é testado no notebook, sem ESP-IDF nem ROS. No firmware, para as classes que o `test/host` compila, um
  include da plataforma vira erro de compilação.
- Um medidor ou critério de verificação é testado com dados sintéticos de resposta conhecida antes de julgar o
  sistema, e fica separado do que mede, como pede a ADR 028.
- Os ensaios (V-NN) verificam o conjunto montado; os testes do domínio só antecipam os erros dele.

## Nota

A classificação de cada arquivo está em `codigo.md`.
