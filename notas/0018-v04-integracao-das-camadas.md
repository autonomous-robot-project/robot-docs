# V-04, integração das camadas - 2026-10-31 - commits 8a44bb0 (robot-ros-system, branch frente-c)

## Launch do deliberador: o spike 0003 refeito no repositório - frente C

Montagem:
- RPi 5, sem ESP32. `ros2 launch robot_bringup deliberator_test.launch.py` (M servido do pacote, Theta*,
  costmap estática + inflação, map → odom estático, `odom_to_tf_ros2` 1.1.1 compilado no `~/robot_ws`).
- Sem odometria, o odom → base_link veio de um `static_transform_publisher` lançado à mão (T3, fora do launch).
- `ComputePathToPose` de p₀ a p_g = (2, 2), `/plan` gravado em bag, analisado com o `analyze.py` do spike.

Medido:
- `error_code` 0, status SUCCEEDED, 69 pontos, sem nó sobrando após SIGTERM ao grupo de processos.
- Vértices brutos (colinearidade de 1e-9 a 0,05 rad): (−0,025; −0,025) · (0,275; 1,675) · (0,325; 1,725) ·
  (0,525; 1,825) · (0,675; 1,825) · (1,925; 1,925) · (1,975; 1,975), os mesmos do spike 0003.
- Com as pontas da ADR 034 (primeiro descartado, vizinho do objetivo removido, último trocado por p_g): trechos
  1,697 · 0,292 · 0,150 · 1,337 m e giros +80,7° · −49,7° · −31,0° · +7,5°, iguais à nota 0003.

Ajustes:
- Sem `update_frequency`, `publish_frequency` e `cost_scaling_factor` do spike: o plano não mudou.

Surpresas:
- O costmap só ativa com o base_link no TF ("Timed out waiting for transform from base_link to map" até o TF
  estático subir): sem o `odom_to_tf_ros2`, o deliberador não sobe sozinho.

Pendências:
- A cadeia real, com a odometria do controlador no `odom_to_tf_ros2`.

## Sistema completo sem potência, parte 1 - frente C

Montagem:
- robot-ros-system 495b196. ESP32 pelo UART, chave dos motores desligada.
- Agente e sequenciador (`mission:=v01`), os dois com `chrt -f 50` e sem launch (`arquitetura.md`, launch). `deliberator_test.launch.py`
  à parte.

Medido:
- `ps -eLo cls,rtprio`: todas as threads do agente e do sequenciador, inclusive as do DDS, em FF 50. `planner_server`,
  `map_server`, `odom_to_tf` e `lifecycle_manager` em TS (ADR 039).
- odom → base_link vindo da Odometria do controlador, a 20,0 Hz. Costmap ativo e `planner_server` `active`.
- `ComputePathToPose` de (0, 0) a (2, 2) com `use_start`: SUCCEEDED, `error_code` 0.
- O sequenciador comandou TWIST(0,2, 0) e abortou 1,3 s depois, em TWIST(0, 0). Sem VM, a roda não gira; o motivo
  provável é a roda travada detectada pelo firmware (não conferido).

Pendências:
- A missão por plano no sequenciador e o smoke test do plano até o eco do controlador.

## Regra da ADR 034 no `check_v04` (V-04, ADR 034) - frente A

Montagem:
- robot-ros-system fc90a05 e 686d441 (`check_v04`), 70f2980 (`plan.py` do sequenciador). Sem hardware.

Decisões:
- O `check_v04` (T1) reescreve a regra da ADR 034 a partir do texto e não importa nada do `robot_sequencer` (T2):
  importando, o instrumento julgaria o sequenciador pelo próprio código dele.
- "Remove o vértice vizinho dele" lido como: o último vértice antes da célula do objetivo sai se estiver numa
  célula adjacente a ela, em linha reta (res) ou na diagonal (√2·res). No `check_v04`, o limiar é
  √2·res + 1e-6 m; a margem cobre o arredondamento em float32 dos centros de célula do planner (~1e-7 m a 2 m).
- map → odom identidade no `/tf_static` é condição de validade do ensaio, e não parte do critério: o plano está em
  map e os alvos do eco em odom, e só com a identidade eles se comparam diretamente.

Conferido:
- O `plan.py` do sequenciador faz a mesma leitura, com limiar 1,5·res. Os dois limiares ficam entre √2·res e
  2·res, então classificam igual todo vértice no centro de uma célula. A ADR 034 não precisa de emenda.
- Sobre o `Path` da seção da frente C acima, a regra do `check_v04` dá os mesmos 4 trechos (1,697 · 0,292 · 0,150 ·
  1,337 m).

## Deriva pelos carimbos da Odometria: prévia em bags de bancada (ADR 027) - frente A

Montagem:
- `measure_clock_drift` (robot-ros-system 686d441) e scripts descartáveis, no notebook, sobre três bags já gravados:
  `f8i6_c1_seco` (frente B, 2/11 18:28, firmware 6879224, 80 s), `v07_f6i6` (frente A, 2/11 18:02, firmware
  6879224, 80 s, com reinícios do ESP32) e `evidencias/V-01/2026-10-31_smoke/nominal` (31 s).
- Resíduo = intervalo entre carimbos consecutivos menos o múltiplo de T_c mais próximo; fase = carimbo módulo T_c.

Medido, com o `measure_clock_drift` (resíduo acima do limiar = ressincronização):

| Bag | Saltos acima de 10 µs (esperados) | Deriva |
| --- | --- | --- |
| `f8i6_c1_seco` | 292 (7 ± 1) | −10,1 ppm, INVALID |
| `v07_f6i6` | 264 (7 ± 1) | +24,3 ppm, INVALID |
| V-01 `nominal` | 218 (3 ± 1) | +2,1 ppm, INVALID |

Medido, pelo mínimo da fase em janelas de 1 s:
- `f8i6_c1_seco`: o mínimo fica plano (±6 µs) entre ressincronizações e salta a cada 10 s: −267 · −93 · +54 · −104
  · −35 · −21 · −322 µs (desvio padrão ~130 µs). Deriva −11,4 ppm em 69 s.
- V-01 `nominal`: dois saltos, deriva −19 ppm em 19 s (incerteza de ~±10 ppm com saltos de ±100 µs em 19 s).
- `v07_f6i6`: saltos de +4368 e −3185 µs nos reinícios; inválido para a deriva.

Surpresas:
- A premissa da nota da ADR 027 (carimbos a múltiplos exatos de T_c entre ressincronizações) não vale. O carimbo é
  `rmw_uros_epoch_nanos() − (esp_timer_get_time() − t_k)` (robot-firmware `session.cpp`): o `esp_timer` é lido
  antes do relógio do micro-ROS, e a demora entre as duas leituras (preempção, interrupções) atrasa o carimbo de
  dezenas a centenas de µs, sempre para depois. Por isso o mínimo da fase, e não cada resíduo, mostra o offset.
- O micro-ROS lê `clock_gettime(CLOCK_REALTIME)` (Micro-XRCE-DDS-Client `util/time.c`, ramo POSIX), e o
  `sdkconfig` usa `CONFIG_NEWLIB_TIME_SYSCALL_USE_RTC_HRT`; que esse relógio venha do mesmo temporizador do
  `esp_timer` está a confirmar na documentação do ESP-IDF. Os platôs planos são consistentes com isso.
- O erro de cada ressincronização (~±100 µs) é da ordem da deriva acumulada em 10 s (~110 µs a −11 ppm).

Pendências:
- Decidir o método do `measure_clock_drift` (mínimo da fase por janela) e emendar a nota da ADR 027.
- Medida no bag da V-07 (5 min: incerteza de ~±1 ppm).

## Missão por plano sem potência e checagem da V-04 - 2026-11-02

Montagem: robot-firmware 03c0f35, robot-interfaces 774e892, robot-ros-system e72729d. `deliberator_test.launch.py`, agente e sequenciador com `chrt -f 50`, heartbeat do notebook a
10 Hz.

Sem potência (script descartável `check_f7i3b.sh`):
- Primeira tentativa: `PLAN_FAILED`, error 203 (`START_OUTSIDE_MAP`). A odometria do ESP32 estava em
  (82,3; 6,3) m, acumulada pelos ensaios anteriores com as rodas suspensas; o costmap de ensaio cobre o M. Reiniciar
  o ESP32 (chave desligada) zera a pose: é o "pose em p₀" do procedimento da V-04.
- Depois do reinício: plano de 69 poses com 4 vértices, trechos de 1,697 · 0,292 · 0,150 · 1,337 m, os da nota
  0003. TURN_TO(1,408 rad) no eco; sem VM, `ABORTED on FAULT_COGNIZANT` 1,29 s depois.
- FF 50 no agente e no sequenciador, TS no deliberador (ADR 039).

Com potência e rodas suspensas (`run_v04`, `check_v04`; dados em `evidencias/V-04/2026-11-02_1932/`):
- Eco TWIST → (TURN_TO → GO_TO) × 4 → TWIST, missão `SUCCEEDED` em 24,8 s.
- Distância final a p_g 0,004 m (ε_g = 0,05 m); map → odom identidade; um plano. V-04: PASS.

## Deriva no bag da V-07 - 2026-11-02

`measure_clock_drift` em `evidencias/V-07/2026-11-02_1933/` (348,6 s, 6823 carimbos):

| Medida | Valor |
| --- | --- |
| Deriva | −2,28 ppm (−22,8 µs por período de 10 s) |
| Saltos achados · esperados | 30 · 34 ± 1: validade reprovada, INVALID |
| Saltos: média · desvio-padrão · mínimo · máximo | −12,9 · 235,1 · −527,1 · +363,2 µs |
| Maior resíduo | 526 µs (limite 2500 µs) |

Leituras:
- Com −2,3 ppm, a deriva acumulada em 10 s (~23 µs) fica no limiar dos degraus (20 µs): parte das ressincronizações
  não aparece como salto, e o método não resolve a deriva neste bag. A prévia no bag C1 a seco deu −11,4 ppm
  (~114 µs por 10 s). A deriva fica entre ~2 e ~11 ppm, sem valor medido.
- O erro de cada ressincronização (desvio-padrão de 235 µs, máximo de 527 µs) domina a deriva acumulada no período
  em qualquer dos dois valores. Encurtar o período não reduz o erro dominante.

Decisão (Lucas, 2/11): `CLOCK_SYNC_PERIOD` fica em 10 s. Erro entre os relógios de até ~0,53 ms, contra
T_c = 10 ms e T_seq = 100 ms.
