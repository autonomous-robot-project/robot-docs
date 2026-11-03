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

## Checagem de bancada da V-01 - 2026-11-02

Montagem: robot-firmware 03c0f35, robot-interfaces 774e892, robot-ros-system e72729d. Rodas suspensas, chave dos motores ligada, frente do VL53L0X livre, sem deliberador.
`run_v01` e `check_v01`; dados em `evidencias/V-01/2026-11-02_1940/`. Checagem sobre o HEAD, não a rodada final:
a rodada final roda sobre a tag.

| Execução | Sequência | Resultado |
| --- | --- | --- |
| nominal | S1 TWIST(0,2; 0) 5,5 s; S2 TURN_TO 1,4 s; S3 GO_TO 3,5 s; S4 TWIST(0, 0) | `SUCCEEDED`, eco 19 a 22 ms depois de cada comando |
| falha | S1 TWIST(0,2; 0); roda travada à mão; S4 TWIST(0, 0) a 6,3 s | `ABORTED on FAULT_COGNIZANT` no log; S4 é a primeira mudança depois da ativação |

`check_v01`: RF-01, RF-04 e RF-05 aprovados; os nós antes e depois de cada execução são `/controller`,
`/rosbag2_recorder`, `/run_v01` e `/sequencer`. V-01: PASS.

Leitura: o log do sequenciador passou a dizer o código que dispara cada reação (robot-docs#51).

## Roda disparada na reversão, rodada final - 2026-11-02

Rodada final sobre a v1.0 (firmware 0744c89, robot-ros-system 8ad2968), RPi no cabo, rodas suspensas. Três
tentativas da V-01 sem dado válido: (1) GPIO 7 esquecido aterrado, a nominal abortou por `FAULT_TEST`; (2) a roda
não foi travada durante o S1, o `FAULT_COGNIZANT` só ativou no S3 (RF-04 reprovado pelo `check_v01`, como deve);
(3) a nominal abortou por `FAULT_COGNIZANT` no S2, com as rodas livres.

Na terceira, no TURN_TO de +90° logo depois do S1 a 0,2 m/s, a odometria mediu v = +0,38 m/s e ω = −3 rad/s: roda
esquerda a +0,59 m/s, com referência de cerca de −0,09 m/s. A roda girou para trás em velocidade máxima, medida como
para frente: o sentido travado (ADR 019) só segue o duty com a roda dada como parada (T_vel = 0,3 s sem borda), e a
referência v − ω·b/2 cruzou ±v_min com as duas rampas somadas (0,5 + 0,25 m/s², ~0,19 s), sem parada detectada. Com o
sentido antigo, o PI empurra mais para trás, a roda nunca para e o sentido nunca atualiza. O `FAULT_COGNIZANT`
detectou depois de T_f = 1 s e o sequenciador abortou (RF-02 e RF-04 funcionaram).

Reproduzido no teste de host com o modelo de malha fechada (`test_fast_reversal_with_encoder`): sem a correção, a roda
dispara a −0,624 m/s; com ela, segue −0,090 m/s. Correção (Lucas, 2/11): `WheelSpeed::reference_from_stop` freia a roda
que ainda gira contra o sinal da referência até ela ser dada como parada; ADR 019 emendada. Na partida em sentido
contrário, a roda espera até T_vel; parada, reflexo e vencimento não mudam.

