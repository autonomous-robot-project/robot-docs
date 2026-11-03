# Rodada final das verificações - 2026-11-02 - tag v1.0 (robot-firmware 16ce5dd, robot-ros-system 8ad2968)

Todas as verificações de bancada sobre o mesmo código: robot-firmware 16ce5dd e robot-ros-system 8ad2968 (tag v1.0
nos dois), robot-interfaces 774e892. RPi compilado da tag por `git archive` em `~/final_v1.0`; `versoes.txt` ao
lado de cada bag. Dados em `evidencias/V-NN/2026-11-02_final/` (V-08: `_final_C1` e `_final_C2`).

Montagem: rodas suspensas, chave dos motores ligada (gravação com a chave ligada autorizada pelo Lucas, nota 0009),
bateria 3S em 12,09 V, b = 0,139 m (nota 0018). RPi pelo cabo na rede de casa: no Wi-Fi da casa, depois da queda de
energia, a perda chegou a 35 % e o heartbeat da V-04 caiu (nota 0018); pelo cabo, 0 % de perda e intervalo máximo
do heartbeat de 0,105 s (T_HB = 0,5 s). Heartbeat do notebook ligado na V-04 e desligado na V-08.

| V-NN | Resultado | Números principais | Script |
| --- | --- | --- | --- |
| V-01 | PASS | nominal até S4 (`SUCCEEDED`); falha: ativação no S1 e S4 em seguida | `run_v01`, `check_v01` |
| V-02 | PASS | 3 cortes detectados (ativo em até 2,16 s, inativo em até 1,55 s); reinício pelo watchdog reportado | `run_v02`, `check_v02` |
| V-03 | PASS | 3 anteparos: zero a partir de 1,25 s, retomada em v_r ± 0,03 m/s; nenhuma falta | `run_v03`, `check_v03` |
| V-04 | PASS | 4 pares TURN_TO → GO_TO; distância final a p_g 0,005 m (ε_g = 0,05 m) | `run_v04`, `check_v04` |
| V-05 | PASS | 318,7 s, 0 prazos perdidos; C_max 953 µs, R_max 974 µs (folga de 90,3 % de T_c) | bag da V-07, `check_v05` |
| V-06 | PASS | 30 interrupções, 1 vencimento cada; atraso no ESP32 de 201,7 a 207,7 ms (máx. 210 ms) | `v06_run.sh`, `check_v06` |
| V-07 | PASS | 302 eventos; Δ mediana 9,9 ms, p99 18,3 ms, máx. 19,4 ms (T_seq = 100 ms) | `run_v07`, `check_v07` |
| V-08 C1 | PASS | 566 eventos, Δ máx. 24,2 ms, p99 19,2 ms; 0 prazos perdidos; 598 planos, maior intervalo 1,006 s (T_gap 1,5 s) | `run_v08 C1`, `check_v07`, `check_v05`, `check_v08_c1` |
| V-08 C2 | PASS | Δ máx. 18,3 ms, p99 17,4 ms; 0 prazos perdidos; `throttled=0x0` antes e depois | `run_v08 C2`, `check_v07`, `check_v05` |

Tentativas sem dado válido, antes das versões finais da tag (detalhes nas notas citadas):
- V-04: duas por `HEARTBEAT_LOST` no Wi-Fi com perda; uma por `REFLEX_FRONT_OBSTACLE` transitório; uma por
  `NO_PROGRESS` falso na aceleração, corrigido com T_stall (ADR 036, nota 0018).
- V-01: uma com o GPIO 7 esquecido aterrado (`FAULT_TEST`); duas sem a roda travada no S1; uma com a roda disparada
  na reversão, corrigida no firmware (ADR 019, nota 0016).
Cada correção moveu a tag v1.0, e as verificações já feitas foram refeitas sobre a versão final.

Pendências:
- O `v06_run.sh` (V-06) é um script de bancada fora do repositório, copiado em `evidencias/V-06/2026-11-02_final/`;
  a regra de evidência pede o código em `tools/` ou no `robot_verification`.
- `rqt_graph` e `inspecao.md` da V-09.
