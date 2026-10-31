# Sequenciador comandando o controlador: smoke test da V-01 - 2026-10-31 - robot-ros-system 6253054 e ccd9b91

Teste inicial, não oficial: o nó do sequenciador (`robot_sequencer`, missão `v01`) comandou o controlador pelo
enlace no RPi, com as rodas suspensas. Não substitui o ensaio da V-01 (critérios e `check_v01` ainda por fazer).
Dados, figuras e versões em `evidencias/V-01/2026-10-31_smoke/`; figuras e listas de eventos (`eventos.txt`) pelo
`plot_v01` do `robot_verification`. Tempos pela recepção no bag (relógio do RPi), desde a primeira mensagem.

| Execução | Energia dos motores | O que aconteceu |
| --- | --- | --- |
| `anteparo` | desligada | Anteparo esquecido na frente do VL53L0X: `REFLEX_FRONT_OBSTACLE` ativo desde o início. O nó publicou TWIST(0,2; 0) na primeira Odometria e abortou 9 ms depois, no primeiro Estado do passo |
| `falha` | desligada | TWIST(0,2; 0) a 1,970 s; `FAULT_COGNIZANT` a 3,250 s (1,28 s: rampa até v_min mais T_f, com as rodas paradas); TWIST(0, 0) na mesma amostra do bag |
| `nominal` | ligada | S1 TWIST(0,2; 0) por 5,5 s; S2 TURN_TO π/2 por 1,4 s; S3 GO_TO (1,000; 0,529) por 3,5 s; S4 TWIST(0, 0), `SUCCEEDED`. Pose final (1,001; 0,536), a 7 mm do alvo (ε_d = 50 mm); parado nos 21 s seguintes |

Leituras:

- **Código já ativo na entrada do passo (ADR 037):** a execução `anteparo` mostra a regra de ponta a ponta. A V-01
  exige a frente livre além de d_stop; com o anteparo, qualquer missão aborta no primeiro passo.
- **Eco do comando:** 8 a 10 ms depois de cada publicação nas três execuções, salvo o primeiro eco da `nominal`
  (0,18 s), atrasado pelo gravador, que descobriu o tópico do Estado depois do primeiro comando.
- **θ₁ = π/2 exato:** o rumo ao fim do S1 era 0 exato. A odometria conta bordas (ADR 048) e o rumo anda em degraus
  de ~3,9°; o y = 0,028 m acumulado no S1 mostra um degrau ida e volta.
- **Smoke test no notebook antes da bancada:** nó isolado (`ROS_DOMAIN_ID=77`,
  `ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST`) com Odometria e Estado falsos, para não alcançar o controlador do RPi
  pela rede (ADR 045). Taxa de republicação ociosa: 19,95 a 20,00 Hz.
