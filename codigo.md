# Código: estrutura, criticidade e rastreabilidade

Cada arquivo de código do robot-firmware e do robot-ros-system, com o papel na estrutura, a criticidade e o
requisito e a verificação que pedem por ele. Confira a linha ao criar, mudar, renomear ou remover um arquivo.

- **Estrutura** (ADR 047, nas três camadas). Domínio: a lógica que vem dos requisitos e das ADRs, sem dependência de
  plataforma (no firmware, compila no `test/host` sem ESP-IDF; no RPi, roda sem rclpy). Infraestrutura: periféricos,
  FreeRTOS, micro-ROS, ROS 2 e leitura de bags.
- **Criticidade.** Quanto rigor de verificação o arquivo exige. Depende do papel do arquivo na evidência, não da
  estrutura: um mesmo pino pode ser atuação (T2) ou instrumento de medição (T1).
- Caminhos relativos à raiz de cada repositório. Os testes (`test/`) não entram na tabela: são a verificação dos
  arquivos T1.

| Nível | Critério | O que é aqui | Como se verifica |
| --- | --- | --- | --- |
| **T1, evidência** | Um erro nele altera um resultado citado na monografia **sem ser detectado** | Instrumentos de medição do firmware (Instrumentação, encoder e velocidade), scripts de critério (`check_vNN`) e scripts que tiram números de dados brutos (`tools/`) | Lido linha a linha pelo autor; teste com dados sintéticos e resposta conhecida, com um caso que deve falhar; validação física ou cruzamento com uma medida independente |
| **T2, produto** | Um erro nele aparece no ensaio que o verifica | O resto do código que roda no robô: domínio (controle, supervisão) e infraestrutura (drivers, enlace) | Ensaio da verificação (V-NN) e testes de host do domínio; leitura não exigida |
| **T3, descartável** | Nunca é citado | Exploração: scratchpad, spikes, builds temporários e ensaios inválidos | Nenhuma; não fica no repositório nem nesta tabela. Um resultado obtido com T3 só entra na monografia depois de refeito com o código promovido a T1 |

O código sob teste é T2, não T1: o ensaio é o detector dos erros dele. Só é T1 o que produz o número ou o veredito
do ensaio.

## robot-firmware

| Arquivo | Estrutura | Criticidade | Requisito | Verificação | Observação |
| --- | --- | --- | --- | --- | --- |
| `components/controller/src/control/acceleration_limiter.cpp` | domínio | T2 | RF-01 | V-01, V-02 | ADR 023; teste no host |
| `components/controller/src/control/inverse_kinematics.cpp` | domínio | T2 | RF-01 | V-01 | |
| `components/controller/src/control/forward_kinematics.cpp` | domínio | T2 | RF-01 | V-01, V-04 | velocidade da Odometria |
| `components/controller/src/control/turn_to.cpp` | domínio | T2 | RF-01 | V-01 | ADRs 024 e 030; teste no host |
| `components/controller/src/control/go_to.cpp` | domínio | T2 | RF-01 | V-01 | ADRs 024 e 030; teste no host |
| `components/controller/src/control/wheel_pi.cpp` | domínio | T2 | RF-01 | V-02 | teste no host |
| `components/controller/src/sensing/wheel_speed.cpp` | domínio | T1 | RF-02, RF-03 | V-01, V-02, V-03 | instrumento (velocidade da V-03, odometria) e sob teste; sem teste no host próprio |
| `components/controller/src/sensing/wheel_odometry.cpp` | domínio | T1 | RF-01 | V-01, V-04 | ADR 048; instrumento da pose; teste no host |
| `components/controller/src/sensing/wheel_encoder.cpp` | infraestrutura | T1 | RF-02, RF-03 | V-01, V-02, V-03 | bordas validadas fisicamente (nota 0010) |
| `components/controller/src/sensing/vl53l0x.cpp` | infraestrutura | T2 | RF-03 | V-03 | porte enxuto da Pololu (MIT); nota 0015 |
| `components/controller/src/sensing/front_range_reader.cpp` | infraestrutura | T2 | RF-03 | V-03 | ADR 020; recuperação do I²C na nota 0015 |
| `components/controller/src/sensing/front_range_classifier.cpp` | domínio | T2 | RF-03 | V-03 | ADR 021; tabela de status, S_MIN_VLX e T_S na nota 0015; teste no host |
| `components/controller/src/supervision/wheel_tracking_monitor.cpp` | domínio | T2 | RF-02 | V-02 | o corte do VM é o detector independente; teste no host |
| `components/controller/src/supervision/task_watchdog.cpp` | infraestrutura | T2 | RF-02 | V-02 | ADR 029 |
| `components/controller/src/supervision/deadline_miss_fault.cpp` | domínio | T2 | RNF-01 | V-05 | ADR 028; teste no host |
| `components/controller/src/supervision/watchdog_test_trigger.cpp` | infraestrutura | T2 | RF-02 | V-02 | injeção do laço infinito |
| `components/controller/src/supervision/response_test_trigger.cpp` | infraestrutura | T2 | RNF-03 | V-07 | ADR 049; pino do modo de ensaio |
| `components/controller/src/instrumentation/expiry_meter.cpp` | domínio | T1 | RNF-02 | V-06 | ADR 028 |
| `components/controller/src/instrumentation/deadline_meter.cpp` | domínio | T1 | RNF-01 | V-05 | ADR 028; teste no host com caso que deve falhar |
| `components/controller/src/instrumentation/sequencer_response_meter.cpp` | domínio | T1 | RNF-03 | V-07 | ADR 049; teste no host com casos que devem falhar |
| `components/controller/src/actuation/driver_input.cpp` | infraestrutura | T2 | RF-01 | V-02 | ADR 008, nota 0009 |
| `components/controller/src/actuation/motor_driver.cpp` | infraestrutura | T2 | RF-01 | V-02 | ADR 008, nota 0009 |
| `components/controller/src/controller.cpp` | misto | T1 (trechos) | RF-02, RF-03, RNF-01, RNF-02 | V-02, V-03, V-05, V-06 | infraestrutura: `start`, `run`, `now`; domínio: `control_cycle`, `command_in_force`, `active_faults`, `active_reflexes`, `restrict_by_reflexes`; T1: `record_expiry`, `publish_instrumentation`, o instante de liberação em `run` e o início e o fim em `control_cycle` |
| `components/link/src/link.cpp` | infraestrutura | T2 | todos | `check_link` | ADRs 012, 043 |
| `components/link/src/session.cpp` | infraestrutura | T2 | todos | `check_link` | ADRs 012, 043 |
| `components/link/src/agent.cpp` | infraestrutura | T2 | todos | `check_link` | ADRs 012, 043 |
| `components/link/src/uart_transport.cpp` | infraestrutura | T2 | todos | `check_link` | ADR 043 |
| `components/link/src/message_conversion.cpp` | infraestrutura | T2 | RF-01 | V-01, V-04 | adaptador entre as mensagens e os tipos do controlador (ADR 018); Odometria (ADR 027) |
| `main/main.cpp` | infraestrutura | T2 | todos | todas | só inicia os componentes |
| `tools/encoder_ao/main/main.cpp` | infraestrutura | T1 | | | nota 0010 |
| `tools/encoder_ao/analyze_encoder_ao.py` | domínio | T1 | | | nota 0010 |
| `tools/motor_characterization/main/duty_schedule.cpp` | infraestrutura | T1 | | | nota 0010 |
| `tools/motor_characterization/main/edge_reporter.cpp` | infraestrutura | T1 | | | nota 0010 |
| `tools/motor_characterization/main/main.cpp` | infraestrutura | T1 | | | nota 0010 |
| `tools/motor_characterization/characterize.py` | domínio | T1 | | | K e tau citados (nota 0010) |
| `tools/front_range/main/main.cpp` | infraestrutura | T1 | RF-03 | V-03 | T_S e tabela de status (nota 0015) |
| `tools/front_range/front_range.py` | domínio | T1 | RF-03 | V-03 | T_S e tabela de status citados (nota 0015) |
| `tools/driver_inputs/in21.py` | domínio | T1 | | | nota 0009 (#21) |

## robot-ros-system

| Arquivo | Estrutura | Criticidade | Requisito | Verificação | Observação |
| --- | --- | --- | --- | --- | --- |
| `robot_verification/robot_verification/check_v02.py` | domínio | T1 | RF-02 | V-02 | julga pelas janelas anunciadas, não pela velocidade medida |
| `robot_verification/robot_verification/check_v03.py` | domínio | T1 | RF-03 | V-03 | julga pelas janelas anunciadas, não pelo bit do reflexo (nota 0015, D8); teste com dados sintéticos |
| `robot_verification/robot_verification/check_v01.py` | domínio | T1 | RF-01, RF-04, RF-05 | V-01 | Sₖ pelo comportamento do comando gravado, nunca por dado do sequenciador; S4 pela ordem após a ativação no S1; lista de nós permitida (nota 0016); teste com dados sintéticos |
| `robot_verification/robot_verification/check_v04.py` | domínio | T1 | RF-06, RF-07 | V-04 | regra da ADR 034 reescrita do texto, sem importar o sequenciador; teste com o Path da nota 0003 escrito à mão |
| `robot_verification/robot_verification/measure_clock_drift.py` | domínio | T1 | — | — | deriva entre os relógios (ADR 027, nota) sobre o bag da V-07; teste com deriva e erro de sincronização conhecidos |
| `robot_verification/robot_verification/check_v05.py` | domínio | T1 | RNF-01 | V-05 | sobre a gravação da V-07; perdas pela diferença início–fim, máximos desde o boot como limite superior |
| `robot_verification/robot_verification/check_v07.py` | domínio | T1 | RNF-03 | V-07 | Δ medido pelo controlador (ADR 049), sem cronometrar o sequenciador; teste com casos que devem falhar e inválidos |
| `robot_verification/robot_verification/check_v08_c1.py` | domínio | T1 | RNF-05 | V-08 | só a validade do C1 (plano entregue a cada T_gap, a medir na V-04); o critério é do `check_v05` e do `check_v07` |
| `robot_verification/robot_verification/check_v06.py` | domínio | T1 | RNF-02 | V-06 | |
| `robot_verification/robot_verification/recording.py` | infraestrutura | T1 | | todas | leitura do bag, veredito, `ControllerRecording` (comando, Estado, Instrumentação, Odometria), marcadores dos procedimentos e buracos na gravação |
| `robot_verification/robot_verification/measure_link_load.py` | infraestrutura | T1 | | | orçamento da ADR 025 (nota 0006) |
| `robot_verification/robot_verification/measure_closed_loop.py` | domínio | T1 | RF-01, RF-02 | | parada após T_vel, v_min sem ciclo-limite (nota 0011) |
| `robot_verification/robot_verification/run_v02.py` | infraestrutura | T2 | RF-02 | V-02 | erro invalida a rodada, e o `check_v02` detecta |
| `robot_verification/robot_verification/run_v03.py` | infraestrutura | T2 | RF-03 | V-03 | erro invalida a rodada, e o `check_v03` detecta |
| `robot_verification/robot_verification/run_v01.py` | infraestrutura | T2 | RF-04, RF-05 | V-01 | conduz as duas execuções, um bag por execução, e salva `ros2 node list` no início e no fim de cada uma (nota 0016) |
| `robot_verification/robot_verification/run_v04.py` | infraestrutura | T2 | RF-06, RF-07 | V-04 | pede o plano por `/goal_pose`, como na operação; erro invalida ou reprova a rodada, e o `check_v04` detecta |
| `robot_verification/robot_verification/run_v07.py` | infraestrutura | T2 | RNF-03 | V-07 | só conta os eventos para parar; erro invalida a rodada, e o `check_v07` detecta |
| `robot_verification/robot_verification/run_closed_loop.py` | infraestrutura | T2 | RF-01, RF-02 | | erro invalida a rodada, e o `measure_closed_loop` detecta |
| `robot_verification/robot_verification/plot_clock_drift.py` | infraestrutura | T2 | | | figuras da deriva entre os relógios (ADR 027); os números vêm do `measure_clock_drift` |
| `robot_verification/robot_verification/plot_closed_loop.py` | infraestrutura | T2 | | | figuras da nota 0011; os números vêm do `measure_closed_loop` |
| `robot_verification/robot_verification/plot_recording.py` | infraestrutura | T2 | | | uma figura por campo gravado dos tópicos do controlador (nota 0013); os números vêm do check |
| `robot_verification/robot_verification/plot_v01.py` | infraestrutura | T2 | RF-04 | V-01 | figura no tempo (comportamento e eco, v, ω, θ, máscaras) e trajetória de uma execução da V-01, mais a lista de eventos (nota 0016); o veredito vem do `check_v01` |
| `robot_verification/bench/v05_bench.sh` | infraestrutura | T2 | RNF-01 | V-05 | checagem da cadeia do medidor (nota 0013); erro invalida a rodada, e o `check_v05` detecta |
| `robot_verification/bench/behaviors_bench.sh` | infraestrutura | T2 | RF-01 | V-01 | primeiro ensaio de TURN_TO e GO_TO (nota 0014); como rodou |
| `robot_verification/bench/reversal_bench.sh` | infraestrutura | T2 | RF-01 | V-02 | reversão isolada (nota 0014); como rodou |
| `robot_verification/bench/reversal_bench.py` | infraestrutura | T2 | RF-01 | V-02 | publica a reversão (nota 0014); como rodou, fora do Ruff |
| `robot_verification/bench/behaviors_series.sh` | infraestrutura | T2 | RF-01 | V-01, V-02 | série antes e depois do T_vel (nota 0014); como rodou |
| `robot_verification/bench/behaviors_series.py` | domínio | T1 | RF-01 | V-01 | conduz e mede os erros finais de TURN_TO e GO_TO (nota 0014); como rodou, fora do Ruff |
| `robot_verification/bench/analyze_behaviors.py` | domínio | T1 | RF-01, RF-02 | V-01, V-02 | disparos, falhas e prazos dos bags da nota 0014 |
| `robot_verification/robot_verification/check_link.py` | infraestrutura | T2 | | | precondição de bancada |
| `robot_verification/robot_verification/link.py` | infraestrutura | T2 | | | QoS, agente (com `chrt`, ADR 039), sequenciador e gravador do bag compartilhados |
| `robot_bringup/launch/deliberator_test.launch.py` | infraestrutura | T2 | RF-05, RF-06 | V-04, V-09 | deliberador na configuração de ensaio; ADRs 026 e 035 |
| `robot_bringup/config/deliberator_test.yaml` | infraestrutura | T2 | RF-06 | V-04 | Theta* e costmap sem camada de obstáculo; ADRs 041 e 042; configuração de ensaio no `arquitetura.md` (launch) |
| `robot_bringup/maps/make_map_m.py` | domínio | T2 | RF-06 | V-04 | gera o M da V-04; `m.pgm` e `m.yaml` versionados (nota 0003) |
| `robot_bringup/launch/deliberator_c1.launch.py` | infraestrutura | T2 | RNF-05 | V-08 | deliberador do C1: o de ensaio da V-04 mais o LiDAR e o SLAM como carga; ADR 040, F8 D1 |
| `robot_bringup/config/slam_load.yaml` | infraestrutura | T2 | RNF-05 | V-08 | `slam_toolbox` do C1 com frame e tópico próprios, sem TF; ADR 040 |
| `robot_bringup/config/slam.yaml` | infraestrutura | T2 | RNF-05 | V-08 | `slam_toolbox` em toda configuração (base_link, `lifecycle_manager`); ADR 040 |
| `robot_bringup/launch/lidar.launch.py` | infraestrutura | T2 | RNF-05 | V-08 | driver do LD19 e base_link → laser, fonte única da pose do laser (#25) |
| `robot_bringup/launch/robot.launch.py` | infraestrutura | T2 | RF-05, RF-06, RF-07 | V-09 | robô inteiro na configuração de operação; fora dos ensaios (configuração de ensaio no `arquitetura.md`, launch), fonte do `rqt_graph`; ADRs 039, 040 e 041 |
| `robot_bringup/config/deliberator_operation.yaml` | infraestrutura | T2 | RF-06 | V-09 | camada de obstáculo sobre o de ensaio; ADRs 040 e 041 |
| `robot_sequencer/robot_sequencer/geometry.py` | domínio | T2 | RF-04 | V-01, V-04 | ponto, pose e ângulo em odom (ADR 047); teste unitário. Nenhum `check_vNN` usa dado interno do sequenciador (V-01) |
| `robot_sequencer/robot_sequencer/mission.py` | domínio | T2 | RF-04, RF-07 | V-01, V-04 | vocabulário das missões: comando, alvos (`Offset`, `MapPoint` convertido na entrada do passo), términos (ε_θ e ε_d da V-01, nota 0014), códigos, reações (abort, ignore, recover), `wait_until_clear` e `TF_MISSING` só com abort (ADRs 032, 035, 036, 037, 038, 047); teste unitário |
| `robot_sequencer/robot_sequencer/sequencer.py` | domínio | T2 | RF-04, RF-05, RF-07 | V-01, V-04, V-07 | motor: passo em execução, término na mensagem da sua entrada, ativação de código com a reação do passo, da missão ou o aborto; `recover` e reentrada; giro acima de θ_max em partes e `NO_PROGRESS`; monitores do eco (T_eco), do enlace (T_LINK) e do heartbeat (T_HB) (ADRs 032, 033, 036, 037, 038, 047); teste unitário |
| `robot_sequencer/robot_sequencer/missions.py` | domínio | T2 | RF-04, RF-05, RF-07 | V-01, V-04, V-07 | missões como dado: as de ensaio pelo parâmetro `mission` e a por plano, um par TURN_TO → GO_TO por vértice (ADRs 032, 034, 038); regras e tabela no cabeçalho; teste unitário |
| `robot_sequencer/robot_sequencer/plan.py` | domínio | T2 | RF-07 | V-04 | vértices do plano: direção que muda no `Path` do Theta*, pontas e absorção de trecho < 2·ε_g com desvio ≤ res/2 (ADRs 034, 041, 042, 047); teste unitário com o `Path` da nota 0003 |
| `robot_sequencer/robot_sequencer/sequencer_node.py` | infraestrutura | T2 | RF-04, RF-06, RF-07, RNF-03 | V-01, V-04, V-07 | nó único em uma thread: Estado, Odometria e `/heartbeat` → `Sequencer`, publicação na transição, timer que confere as idades e republica a f_cmd, relógio monotônico; bit desconhecido vira `Code.UNKNOWN`; com `mission` vazio, `/goal_pose` → `ComputePathToPose` assíncrono com descarte da resposta antiga (`PlanClient`) e map → odom do tf2 com timeout zero (ADRs 025, 031, 033, 034, 035, 037) |
