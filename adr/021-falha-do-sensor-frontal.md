---
data: 2026-10-23
status: provisório
camada: "controlador"
revoga:
revogada_por:
affects: []
evidence: [V-03, V-09]
---
# 021 – Falha do sensor frontal tratada como obstáculo

## Problema

O reflexo de obstáculo frontal depende do VL53L0X. O controlador precisa reagir quando não tem leitura confiável, sem depender das demais camadas (RF-03). Status não nulo nem sempre é falha: "sem alvo no alcance" é o resultado normal com o caminho livre.

## Decisão

A cada ciclo, a leitura do sensor é classificada em um de três estados:

- **obstáculo:** medida válida abaixo de D_STOP, ou alvo abaixo do alcance mínimo;
- **livre:** medida válida em D_STOP ou acima, ou sem alvo no alcance;
- **falha:** nenhuma leitura classificável há mais de T_S.

A falha é tratada como obstáculo: avanço da referência igual a zero, com giro e ré permitidos. A falha é reportada ao sequenciador. No boot, antes da primeira leitura válida, o estado é falha.

## Alternativa descartada

- **Parada total:** bloqueia o giro, que o sensor não cobre, sem ganho de segurança, e tira opções de recuperação do sequenciador.
- **Só reportar:** viola o RF-03, porque o reflexo passaria a depender do sequenciador.
- **Todo status não nulo como falha:** o robô deixaria de avançar em espaço aberto.

## Racional

- O controlador só restringe o comando, nunca o amplia. A falha dispara o mesmo reflexo de obstáculo frontal, sem mecanismo novo.
- Atende à falha cognizante de Gat: a perda do sensor é detectada e reportada, e o sequenciador decide a recuperação.
- T_S tolera leituras ruins isoladas sem bloquear o avanço a cada uma.

## Nota

O valor de T_S será fixado por medição.
