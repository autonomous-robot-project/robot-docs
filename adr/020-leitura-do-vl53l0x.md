---
data: 2026-10-23
status: provisório
camada: "controlador"
revoga:
revogada_por:
affects: []
evidence: [V-03, V-05]
---
# 020 – Leitura do VL53L0X em tarefa própria

## Problema

A leitura do VL53L0X exige espera no barramento I²C. O sensor produz uma medida nova a cada ≈ 20 a 33 ms. A tarefa de controle, com período de 10 ms, não pode esperar por I/O (RNF-01).

## Decisão

Uma tarefa de sensor, sem tempo real e com prioridade acima da micro-ROS, lê o VL53L0X no ritmo do próprio sensor. Ela publica num canal de último valor (ADR 017) três dados: distância, status e instante da medida.

A tarefa de controle lê esse canal sem esperar. O controlador passa a ter três tarefas: controle, sensor e micro-ROS. A tarefa de controle fica fixada no núcleo 1; as tarefas de sensor e micro-ROS, no núcleo 0.

## Alternativa descartada

- **Leitura na tarefa de controle, com espera limitada a T_I2C:** põe I/O e a recuperação do barramento dentro do prazo rígido, sem reduzir a latência do reflexo.
- **Interrupção por limiar (pino INT):** sozinha, falha para o lado inseguro, porque ausência de interrupção é lida como caminho livre. Também não dispensa I²C para limpar e rearmar o pino. Somada a esta decisão, ganharia ≈ 1 mm de distância de parada por 0,1 m/s de v_max.

## Racional

- Gat exige tempo limitado por iteração do controlador. Com esta decisão, o laço não faz I/O.
- A latência do reflexo é limitada pelo ritmo de medida do sensor, não pela frequência de leitura no laço.
- A tarefa de sensor não precisa de tempo real. Se ela atrasar ou travar, a medida envelhece, e o controlador percebe pela idade. Assim a falha do sensor do reflexo continua detectável no próprio controlador (RF-03).

## Nota

- Reabre a decisão "duas tarefas" do controlador.
- A reação à falha do sensor (idade ou status inválido) é a questão 4b.
- O uso do pino INT fica como issue no `robot-docs`, condicionado ao ensaio de latência do reflexo.
