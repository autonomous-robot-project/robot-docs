# V-08, isolamento do deliberador - 2026-10-31 - commits 495b196 e a9fd73d (robot-ros-system)

## LD19 e SLAM como carga do C1 - frente C

Montagem:
- `ros2 launch robot_bringup deliberator_c1.launch.py`: o launch de ensaio da V-04 mais o driver do LD19, o
  base_link → laser e o `slam_toolbox` 2.8.5, com `/slam_map`, frame `slam_map` e sem TF (ADR 040).
- O odom → base_link vem de um `static_transform_publisher` lançado à mão.
- LD19 pelo adaptador CP2102 em `/dev/ttyUSB0`. Pose do laser em base_link: x_l, y_l, z_l e ψ_l a medir (#25); no launch, 0.

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
- Pose do laser (#25).
- O `run_v08` espera ≥ 5 s no encerramento ou usa SIGINT.

## Launch de operação sem potência - frente C

Montagem:
- robot-ros-system 8224f8c. `ros2 launch robot_bringup robot.launch.py` com ESP32 pelo UART e LD19; chave dos
  motores desligada. Sequenciador do HEAD 8224f8c, sem a missão por plano.
- O C1 foi conferido de novo depois da troca para o `lidar.launch.py` e o `slam.yaml`: os três nós `active`,
  `/slam_map` sem TF, plano de (0, 0) a (2, 2) SUCCEEDED.

Medido:
- `ps -eLo cls,rtprio`: agente em FF 50; SLAM, driver, planner, `odom_to_tf` e `lifecycle_manager` em TS.
- `slam_toolbox` e `planner_server` `active` pelo mesmo `lifecycle_manager`. Costmap com
  `static_layer`, `obstacle_layer` e `inflation_layer`. `/map` do SLAM com 45 × 47 células de 0,05 m; map → odom
  publicado pelo SLAM; `/scan` a 10,0 Hz.
- Plano de (1,00; 0,54), a pose da odometria, a (0,5; 0): ABORTED, partida ou objetivo em obstáculo. Só
  informação: com as rodas suspensas a odometria anda e o mapa não.
- Encerramento por SIGINT: todos os processos saem em 0,5 s.

Surpresas:
- O sequenciador morre na partida: o HEAD não aceita `mission` vazio (`ValueError`). A missão por plano ainda não
  estava no sequenciador (frente B).
- Em shell não interativo, processo lançado com `&` herda o SIGINT ignorado. O `ros2 launch` e o agente não
  respondem ao SIGINT, e os nós rclpy/rclcpp respondem (instalam tratador próprio). Num terminal, o Ctrl-C funciona.
  Script que encerra um launch por SIGINT precisa restaurar o tratamento padrão antes do `exec` ou usar SIGTERM.

Pendências:
- Conferir o sequenciador no `robot.launch.py` depois da missão por plano.

## T_gap da validade do C1 - frente A

Montagem:
- Bag `f8i6_c1_seco` (frente B, 2/11 18:28, 80 s, firmware 6879224), cópia no notebook. `check_v08_c1`
  (robot-ros-system d7285ec) e script descartável dos intervalos entre planos.
- No C1, o sequenciador pede um plano novo a cada resposta: o intervalo entre dois `/plan` é a duração de um
  `ComputePathToPose` sob a carga do SLAM, mais o novo pedido.

Medido:

| Medida (3188 planos) | Valor |
| --- | --- |
| Intervalo entre planos: mediana · p99 · p99,9 · máximo | 22,6 · 77,1 · 107,0 · 132,2 ms |
| Primeiro plano depois do primeiro Instrumentation | 0,423 s |
| Último Instrumentation depois do último plano | −0,035 s |

Decisões:
- T_gap = 0,5 s: cobre o primeiro plano a 0,42 s do início da gravação (provavelmente a descoberta do `/plan` pelo
  gravador, a confirmar) e fica a 3,8 vezes o maior intervalo. Com ele, o `check_v08_c1` dá o C1 estabelecido nesse
  bag.
- A calibração vem deste bag a seco, e não do bag da V-04, como previsto: o `run_v04` não grava o instante do
  pedido (o pedido é interno ao sequenciador), e um só planejamento, sem SLAM, não dá base para o limiar.

Pendências:
- Conferir no C1 de 10 min que o maior intervalo fica abaixo de T_gap; se passar perto, rever com o bag.
