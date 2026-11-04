# TURN_TO, GO_TO e o sentido perdido na reversão - 2026-10-28 - commits 87cc48b e 1eb42d6 (firmware gravado), robot-ros-system bench/

Ferramentas: robot-ros-system/robot_verification/bench: `behaviors_bench.sh` (primeiro ensaio), `reversal_bench.sh`
e `.py` (reversão isolada), `behaviors_series.sh` e `.py` (série: 10 reversões, 7 TURN_TO, 3 GO_TO, com alvos
relativos à Odometria), todos como rodaram; `analyze_behaviors.py` (análise dos bags). Evidências:
evidencias/nota-0014/2026-10-28/ (quatro bags, `*_analise.txt`, `*_saida.txt`).

Montagem: a da nota 0013, rodas suspensas, chave dos motores ligada só durante cada ensaio.

Enlace com a Odometria (87cc48b, chave desligada): `check_link` PASS (a primeira rodada, logo depois de gravar,
falhou sem Estado em 10 s e não se repetiu depois de esperar 3 s após o reset); ESP32 → RPi 22,0 % e RPi → ESP32
1,0 % (orçamento de 50 %); Odometria a 20 Hz, quadros de 732 B aceitos pelo agente com MTU de 1024 B (ADR 043);
recepção − carimbo de 16,5 a 16,9 ms, positivo e estável (ADR 027).

Primeiro ensaio (87cc48b, T_vel = 0,51 s): o TURN_TO(π/2) passou do alvo (97,5°) e caçou; a roda esquerda leu
+0,51 a +0,65 m/s com referência ≤ 0, inclusive depois do vencimento (TWIST(0, 0)): a roda girava para trás com o
sentido travado em +1, a realimentação ficou positiva e o duty saturou. Parou quando a referência entrou em ±v_min
(zona morta, ADR 030). O GO_TO seguinte ficou parado: alvo atrás (e_θ ≈ 137°), v = 0 e ω·b/2 abaixo de v_min.
O script deixou ~1,4 s sem comando entre as fases (um `ros2 topic pub` por fase); a série usa um publicador só.

Causa: numa reversão, a rampa (ADR 023) mantém a referência em ±v_min por v_min/a_dec + v_min/a_acel ≈ 0,42 s, e a
tensão reversa chega antes de a roda ser dada como parada (T_vel = 0,51 s sem borda). Se a primeira borda da ré
cai nessa janela, o sentido não é reavaliado (ADR 019). A reversão isolada (±0,15 m/s) escapou: a ré começou
~0,5 s depois da última borda.

Série, antes e depois de T_vel = 0,3 s:

| | T_vel 0,51 s (87cc48b) | T_vel 0,3 s (1eb42d6) |
|---|---|---|
| Reversões ±0,15 m/s com disparo | 2 de 10 (roda direita, +0,37 a +0,40 m/s, 1,2 s cada) | 0 de 10 |
| FAULT_COGNIZANT | 2, ~0,6 s depois de cada disparo | nenhum |
| TURN_TO +90, −90, +45, −45, +170, −170, +30°: erro final | −3,6; +3,6; −1,8; +1,8; −1,6; +1,6; +2,7° | iguais |
| TURN_TO: tempo até parar | 2,0 a 3,1 s | 1,9 a 2,9 s |
| GO_TO 1 m; 1 m com 0,3 m de lado, sem alinhar; 2 m: distância final | 1, 5, 1 mm | 6, 5, 1 mm |
| GO_TO: tempo até parar | 6,8; 7,1; 11,8 s | 6,7; 6,9; 11,6 s |
| C_max / R_max (desde o boot); prazos perdidos | 840 / 866 µs; 0 | 803 / 824 µs; 0 |

Leituras:

- O erro final do TURN_TO fica no previsto pela ADR 030 (~3,7° com v_min = 0,07 m/s); a resolução da Odometria em
  giro é de 3,9° por borda de uma roda (s/L_rodas). O GO_TO para a ≤ 6 mm do alvo (previsto ~5 mm) e corrige 17° de
  rumo inicial pelo sin e_θ.
- O ciclo-limite do primeiro ensaio veio do disparo, não da resolução: com o sentido certo, os sete giros pararam
  sem caçar.
- A falha cognizante pegou os dois disparos (V-02), como reserva.
- Com os comportamentos no ciclo, R_max ≤ 866 µs: margem de 91 % sobre T_c (nota 0013: 441 µs só com TWIST).

Ajustes:

- T_vel = 0,3 s (era 0,51 s, da detecção; confirmado na nota 0011 só em TWIST para frente): T_vel + 50 ms de parada
  < 0,42 s, com static_assert no `control_config.h`; T_vel > s/v_min = 0,15 s. A detecção da V-02 só fica mais
  rápida. Emendas na ADR 019 e no V-02_calculo_encoder.md.

Pendências: os 0,42 s de freio em cada reversão (#47).
