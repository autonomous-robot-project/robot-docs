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
