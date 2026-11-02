# V-04, integração das camadas - 2026-10-31 - commits 8a44bb0 (robot-ros-system, branch frente-c)

## Launch do deliberador: o spike 0003 refeito no repositório (F7 I1) - frente C

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
- F7 I3: a cadeia real, com a odometria do controlador no `odom_to_tf_ros2`.

## Sistema completo sem potência (F7 I3, parte 1) - frente C

Montagem:
- robot-ros-system 495b196. ESP32 pelo UART, chave dos motores desligada.
- Agente e sequenciador (`mission:=v01`), os dois com `chrt -f 50` e sem launch (F7 I3). `deliberator_test.launch.py`
  à parte.

Medido:
- `ps -eLo cls,rtprio`: todas as threads do agente e do sequenciador, inclusive as do DDS, em FF 50. `planner_server`,
  `map_server`, `odom_to_tf` e `lifecycle_manager` em TS (ADR 039).
- odom → base_link vindo da Odometria do controlador, a 20,0 Hz. Costmap ativo e `planner_server` `active`.
- `ComputePathToPose` de (0, 0) a (2, 2) com `use_start`: SUCCEEDED, `error_code` 0.
- O sequenciador comandou TWIST(0,2, 0) e abortou 1,3 s depois, em TWIST(0, 0). Sem VM, a roda não gira; o motivo
  provável é a roda travada detectada pelo firmware (não conferido).

Pendências:
- A missão por plano (F7 I2) e o smoke test (F7 I4).

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
