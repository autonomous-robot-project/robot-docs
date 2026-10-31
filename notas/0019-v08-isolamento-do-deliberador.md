# V-08, isolamento do deliberador - 2026-10-31 - commits 495b196 e a9fd73d (robot-ros-system)

## LD19 e SLAM como carga do C1 (F8 I1, F8 I2) - frente C

Montagem:
- `ros2 launch robot_bringup deliberator_c1.launch.py`: o launch de ensaio da V-04 mais o driver do LD19, o
  base_link → laser e o `slam_toolbox` 2.8.5, com `/slam_map`, frame `slam_map` e sem TF (ADR 040).
- O odom → base_link vem de um `static_transform_publisher` lançado à mão.
- LD19 pelo adaptador CP2102 em `/dev/ttyUSB0`. Pose do laser em base_link: x_l, y_l, z_l e ψ_l a medir (F8 I0,
  #25); no launch, 0.

Medido:
- `/scan`: 9,80 Hz em 100 varreduras; intervalo de 0,100 a 0,200 s, desvio padrão de 0,014 s. De 502 a 503 pontos
  por volta, incremento de 0,717°, de 417 a 423 válidos.
- `slam_toolbox` ativado pelo `lifecycle_manager_slam`. `/slam_map` com 55 × 47 células; nenhuma mensagem com
  `slam_map` em 4 s de `/tf`.
- Planner ativo com o SLAM no ar: plano de (0, 0) a (2, 2) SUCCEEDED.
- Encerramento: com SIGINT ao launch, o driver sai em 0,29 s e o resto em 3,6 s.

Ajustes:
- O driver v3.0.3 não compila com o GCC 13.3. Remendo de uma linha (`#include <pthread.h>`), registrado no README
  do robot-ros-system.
- 14 pacotes apt novos (`slam_toolbox` e dependências) em hold.

Pendências:
- Pose do laser (F8 I0, #25).
- O `run_v08` espera ≥ 5 s no encerramento ou usa SIGINT.
