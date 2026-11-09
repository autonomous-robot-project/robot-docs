# Rodada final das verificações - 2026-11-02 - tag v1.0.0 (robot-firmware 16ce5dd, robot-ros-system 8ad2968)

Todas as verificações de bancada sobre o mesmo código: robot-firmware 16ce5dd e robot-ros-system 8ad2968 (tag v1.0.0
nos dois), robot-interfaces 774e892. RPi compilado da tag por `git archive` em `~/final_v1.0`; `versoes.txt` ao
lado de cada bag. Dados em `evidencias/V-NN/2026-11-02_final/` (V-08: `_final_C1` e `_final_C2`).

Montagem: rodas suspensas, chave dos motores ligada (gravação com a chave ligada autorizada pelo Lucas, nota 0009),
bateria 3S em 12,09 V, L_rodas = 0,139 m (nota 0018). RPi pelo cabo na rede de casa: no Wi-Fi da casa, depois da queda de
energia, a perda chegou a 35 % e o heartbeat da V-04 caiu (nota 0018); pelo cabo, 0 % de perda e intervalo máximo
do heartbeat de 0,105 s (T_HB = 0,5 s). Heartbeat do notebook ligado na V-04 e desligado na V-08.

| V-NN | Resultado | Números principais | Script |
| --- | --- | --- | --- |
| V-01 | PASS | nominal até S4 (`SUCCEEDED`); falha: ativação no S1 e S4 em seguida | `run_v01`, `check_v01` |
| V-02 | PASS | 3 cortes detectados, dentro das tolerâncias de 2,16 s (ativo) e 1,55 s (inativo); reinício pelo watchdog reportado | `run_v02`, `check_v02` |
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
Cada correção moveu a tag v1.0.0, e as verificações já feitas foram refeitas sobre a versão final.

Pendências:
- O `v06_run.sh` (V-06) é um script de bancada fora do repositório, copiado em `evidencias/V-06/2026-11-02_final/`;
  a regra de evidência pede o código em `tools/` ou no `robot_verification`.

## V-09, inspeção de código - 2026-11-02

`inspecao.md` (21 itens do critério com arquivo:linha na tag, 5 parâmetros conformes) e `rqt_graph.png` do
`robot.launch.py` com o sistema completo no RPi, em `evidencias/V-09/2026-11-02_final/`. No grafo, o
`/controller/command` tem só o `/sequencer` como publicador, e o `/planner_server` só se liga ao `/sequencer`, pela
action `compute_path_to_pose` (RF-07). Divergência aceita (Lucas, 2/11): o gatilho do watchdog da V-02 trava o ciclo
num laço sem limite só com o pino aterrado à mão (ADR 029). Os scripts de ensaio do `robot_verification` também
publicam o comando, fora do `robot.launch.py`. V-09: PASS.

## Figuras para a monografia - 2026-11-03

`plot_final_round` (robot_verification) lê os bags da rodada final pelas mesmas classes dos checks e grava PDF
(vetorial) e PNG na pasta de cada verificação:

| Figura | Verificação | O que mostra |
| --- | --- | --- |
| `V-01/2026-11-02_final/fig_v01_selecao` | V-01 | Passos S1–S4 da missão em cada execução e o `FAULT_COGNIZANT`: na falha, o S4 começa na ativação, ainda no S1 |
| `V-02/2026-11-02_final/fig_v02_falha_cognizante` | V-02 | Velocidade das rodas, cortes da chave, `FAULT_COGNIZANT` em cada corte e `FAULT_WATCHDOG_RESTART` depois do GPIO 11 |
| `V-03/2026-11-02_final/fig_v03_reflexo` | V-03 | Velocidade, janelas do anteparo e `REFLEX_FRONT_OBSTACLE`: parada e retomada em cada janela |
| `V-04/2026-11-02_final/fig_v04_plano` | V-04 | M, zona proibida (r + m + res), plano do Theta*, vértices e trajetória da odometria |
| `V-06/2026-11-02_final/fig_v06_vencimento` | V-06 | Atraso do vencimento nas 30 interrupções, entre T_cmd e T_cmd + T_c |
| `V-07/2026-11-02_final/fig_v07_v08_resposta` | V-07, V-08 | Distribuição acumulada de Δ em C0, C1 e C2 contra T_seq |

A V-05 não tem figura (um valor por condição: R_max contra T_c, na tabela acima). Na V-02, os picos de velocidade ao
religar a chave (até 0,55 m/s) não entram no critério; causa provável, não conferida: durante o corte o PI satura em
DUTY_MAX, com a integral no limite da integração condicional (ADR 023), e a roda acelera até o PI sair da saturação.

