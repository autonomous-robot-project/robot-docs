# V-02, falha cognizante na bancada - 2026-10-27 - commits ad3cd2b (firmware gravado) e 8a93227 (robot-ros-system)

Ferramentas: robot-ros-system/robot_verification `run_v02` (conduz e grava o bag) e `check_v02` (critério, T1).
Evidência: evidencias/V-02/2026-10-27/ (bag e saída do check_v02).

Montagem: a da nota 0011 (rodas suspensas, bateria 3S a 12,23 V, fusível de 2 A). Fio solto no GPIO 11 para a
injeção.

Medido (PASS), tempos desde o início da gravação:

| Evento | Anúncio | Falha ativa | Falha inativa |
|---|---|---|---|
| Corte 1 | 12,57 s | 14,14 s (+1,57 s) | 16,13 s (+0,55 s do religamento) |
| Corte 2 | 23,58 s | 25,20 s (+1,62 s) | 27,21 s (+0,63 s) |
| Corte 3 | 34,58 s | 36,07 s (+1,49 s) | 38,10 s (+0,52 s) |
| GPIO 11 no GND | 45,58 s | 1,24 s sem Estado; volta com FAULT_WATCHDOG_RESTART | |

- Tolerâncias do check_v02: ativa até 2,16 s depois do anúncio do corte, inativa até 1,55 s depois do religamento.
- Nenhuma falha na partida; eco de TWIST(0,2, 0) em cada corte; Estado sem lacunas até a injeção.

Ajustes:

- `BagRecorder` aborta se a pasta do bag já existe: o `ros2 bag record` recusa a pasta, e o erro se perdia com o
  stderr. A primeira tentativa do dia foi repetida por isso.

Surpresas: nenhuma.

Pendências: nenhuma.
