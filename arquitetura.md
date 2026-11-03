# Arquitetura

Três camadas (Gat, 1998), em dois processadores:

| Camada | Onde | Natureza | Implementação |
| --- | --- | --- | --- |
| Controlador | ESP32-S3 | Tempo real rígido (T_c = 10 ms) | ESP-IDF + FreeRTOS, micro-ROS |
| Sequenciador | RPi 5 | Rápido, sem garantia rígida (reação < T_seq = 100 ms) | Nó ROS 2 único em Python, SCHED_FIFO |
| Deliberador | RPi 5 | Sem restrição de tempo | Nav2 `planner_server` (Theta*) + `slam_toolbox` |

Enlace: micro-ROS sobre UART a 921600 baud, pelos GPIO, com o agente no RPi (ADRs 012 e 043). O porquê de cada decisão está nas ADRs citadas.

## Invariantes

Toda mudança precisa preservar estas regras:

1. **O controlador só restringe, nunca decide.** Ele converge para o alvo do comportamento ativo, restringe por reflexos e reporta. Término e troca de comportamento são do sequenciador (ADR 024, RNF-04).
2. **Estado do controlador que representa o mundo é filtragem ou expira em tempo limitado.** O comando vence em T_cmd = 200 ms e vira TWIST(0, 0) (RNF-02). A pose odométrica e o sentido travado da roda (ADR 019) são estimação sobre as medidas do encoder, ou seja, filtragem.
3. **Condições são publicadas como estado atual, não como eventos.** O controlador publica máscaras; o sequenciador detecta bordas, conta episódios e decide tentativas (ADRs 025 e 037).
4. **Nada bloqueia o sequenciador.** A consulta ao deliberador é assíncrona, e o planejamento roda em outro processo (ADR 033).
5. **Todo caminho do deliberador ao controlador passa pelo sequenciador.** O deliberador entrega resultados (plano, map → odom), e o sequenciador os converte em comportamentos (RF-07).
6. **Cada camada vigia a de cima:**
   - o watchdog vigia a tarefa de controle (ADR 029);
   - o controlador vigia o sequenciador pelo vencimento do comando;
   - o sequenciador vigia o notebook pelo heartbeat (ADR 016).
7. **O isolamento no RPi vem da prioridade, não de limites no deliberador** (ADR 039).

## Interface ESP32 ↔ RPi

| Sentido | Tópico | Tipo | Taxa | Conteúdo |
| --- | --- | --- | --- | --- |
| RPi → ESP32 | Comando (`/controller/command`) | Próprio | 20 Hz | Comportamento ativo + parâmetros, numa mensagem atômica (ADR 024) |
| ESP32 → RPi | Estado (`/controller/state`) | Próprio | 100 Hz | Máscaras de 32 bits de falhas e reflexos ativos; eco do comando em vigor |
| ESP32 → RPi | Odometria | `nav_msgs/Odometry` | 20 Hz | Pose em `odom`, carimbada no ESP32 com o relógio sincronizado ao agente (ADR 027) |
| ESP32 → RPi | Bateria | `sensor_msgs/BatteryState` | ~1 Hz | Tensão filtrada |
| ESP32 → RPi | Instrumentação | Próprio | 10 Hz | C_max, R_max, prazos perdidos, vencimentos do comando e o atraso do último, acumulados desde o boot; Δ da V-07 (ADR 028) |

- Toda a QoS do enlace é best effort, volatile, profundidade 1, e os consumidores precisam pedir a mesma (ADR 025).
- Os códigos das máscaras são constantes do `robot-interfaces`.
- A ocupação do enlace é de ≈ 20 %, com orçamento de 50 %. Um dado novo entra no Estado, salvo pelos critérios da ADR 025.

**Frames:** map → odom (`slam_toolbox`) → base_link (`odom_to_tf_ros2` no RPi, com o carimbo original; ADR 026) → laser (estático).

## Controlador (ESP32-S3)

### Estrutura

O firmware tem dois componentes ESP-IDF (ADR 018):

- `controlador`: tarefas, sensores, atuação;
- `enlace`: micro-ROS e conversão de mensagens. Depende do `controlador`, nunca o contrário.

| Tarefa | Núcleo | Prioridade | Papel |
| --- | --- | --- | --- |
| Controle | 1 | Mais alta, tempo real | Ciclo de 10 ms |
| Sensor | 0 | Média | Lê o VL53L0X no ritmo do sensor; o I/O e a recuperação do I²C ficam aqui (ADR 020) |
| micro-ROS | 0 | Baixa | Enlace e sincronização de relógio |

Os contextos trocam dados só por canais de último valor: fila do FreeRTOS de um elemento, último valor, um produtor (ADR 017). São quatro: comando, estado, bordas do encoder e sensor frontal. A tarefa de controle nunca espera por eles, e canal de comando vazio vale como comando vencido.

Recuperação do I²C na tarefa de sensor: cada transação tem timeout T_I2C; depois de N_I2C falhas seguidas, a tarefa bloqueia por T_retry e reinicializa o sensor (recupera um sensor que reiniciou em standby por mau contato). A espera é bloqueante, para não tirar o núcleo 0 da micro-ROS. A segurança não depende da recuperação: sem medida nova, ela envelhece e o controlador entra em falha após T_S (ADRs 020 e 021; nota 0015).

### Ciclo de controle (a cada T_c, por `vTaskDelayUntil`)

1. Lê os canais de último valor.
2. Mede velocidade, sentido e odometria a partir das bordas (odometria pela contagem, ADR 048), e a tensão da bateria.
3. O comportamento ativo calcula a referência (v, ω).
4. Restringe pelo vencimento do comando e pelos reflexos. As restrições comutam entre si.
5. Aplica a rampa assimétrica (a_acel < a_dec; ADR 023).
6. Faz a cinemática inversa para a referência de cada roda.
7. PI por roda, com integração condicional, saturação em duty ≤ 48 % e zona morta abaixo de v_min (ADR 030). Os ganhos saem do modelo do motor e do tempo de acomodação t_s: malha de 1ª ordem, sem sobressinal.
8. Escreve o PWM.
9. Monitor de falha (RF-02).
10. Publica nos canais de último valor.

A atuação vem antes da manutenção, para manter constante o atraso entre medida e PWM. O laço não faz I/O, não aloca memória e não tem laço sem limite (RNF-01).

O DRV8871 opera em decaimento lento: a frenagem é o próprio PWM, e duty = 0 é freio total (ADR 023). A frequência do PWM é alta em relação a L/R do motor (ordem de 20 kHz). O PWM vem do LEDC, um canal por pino: o pino do sentido fica em duty 100 % e o outro recebe o PWM invertido. Os dois canais de um driver trocam de duty cada um no início do seu próximo período, então a passagem de roda livre para freio no 1º ciclo após o boot pode dar um pulso de tração de até um período (50 µs). Aceito: estimado em ~0,4 A no motor TT, sem vencer o atrito da caixa; a #21 mede na bancada.

**Garantia de parada:** d_parada(v_max) + v_max·T_S ≤ d_stop ≤ d_sensor, com d_parada ≈ v_max²/(2·a_dec) + latências, e v_max alcançável com a bateria em V_CRIT (ADRs 021 e 023; valores pela issue #27).

### Comportamentos (ADR 024)

| Comportamento | Controla | Parâmetros | Perfil de convergência (ADR 030) |
| --- | --- | --- | --- |
| TWIST | (v, ω) | (v, ω) | — |
| TURN_TO | Rumo | θ em `odom` | ω ∝ √(2·α_dec·\|e_θ\|) |
| GO_TO | Posição | (x, y) em `odom` | v ∝ √(2·a_dec·e_d) · max(0, cos e_θ); ω ∝ sin e_θ · min(1, e_d/d₀) |

O alvo de giro nunca fica a 180° ou mais do rumo atual; o sequenciador garante isso. Toda troca de comportamento passa pela rampa, então nunca é brusca nos motores.

### Encoders (canal único)

- A ISR de GPIO registra o instante das bordas de subida. Uma amostragem a cada 500 µs conta a fenda quando o nível fica
  alto por 2 ms depois de estável em baixo, porque o comparador do sensor oscila nas transições (nota 0010).
- A velocidade é s/Δt, com s = 10,2 mm, e vale zero após T_vel sem borda.
- O sentido fica travado enquanto a roda gira e passa a seguir a tensão aplicada só com a roda parada (ADR 019).

### Reflexos

Todo reflexo restringe a referência e é reportado na máscara correspondente.

| Reflexo | Condição | Efeito |
| --- | --- | --- |
| Obstáculo frontal | Medida válida do VL53L0X < d_stop (nota 0015) | Zera o avanço; giro e ré continuam permitidos (ADR 021) |
| Bateria crítica | Tensão filtrada < V_CRIT | Referência a zero; libera sozinho, sem histerese (ADR 022) |

### Falhas reportadas

| Falha | Detecção |
| --- | --- |
| Falha cognizante | Erro de velocidade acima de e_f por T_f, com referência ≥ v_min |
| Prazo perdido | Detectado em todos os builds; ativo por 200 ms após a última perda (ADR 028) |
| Reinício por watchdog | Watchdog de tarefas sobre a tarefa de controle, com prazo de poucos T_c (ADR 029) |
| Falha do sensor frontal | Só leituras inválidas há mais de T_S = 100 ms, e também no boot (nota 0015). Zera o avanço como o obstáculo frontal (ADR 021) |
| Falha de ensaio | Só no modo de ensaio da V-07, ativado pelo GPIO 7 em nível baixo: ativa a cada T_ev, desativa na chegada do TWIST(0, 0) (ADR 049) |

Os códigos de prazo perdido e de reinício ficam ativos por tempo limitado. A falha do sensor frontal fica em `faults`, não em `reflexes`: a máscara de reflexos reporta condições do ambiente, e o critério da V-03 exige falha inativa (nota 0015).

### Boot seguro

- Pull-downs mantêm os drivers em roda livre no reset e na gravação (ADR 008).
- Canal de comando vazio vale como comando vencido.
- O sensor frontal começa em falha.
- A odometria só é publicada após a primeira sincronização de relógio.

## Sequenciador (RPi 5)

### Modelo

Um nó `rclpy`, um processo, executor de uma thread (ADRs 031 e 033).

Uma missão é `Mission(steps, reactions)`, e um passo é `Step(behavior, until, reactions)` (ADR 032).

#### Andamento da missão

- Os parâmetros do passo são calculados na entrada, a partir da pose atual.
- O predicado `until` é testado na Odometria; satisfeito, o sequenciador avança ao próximo passo.
- Uma borda de subida numa máscara consulta a tabela de reações, primeiro a do passo e depois a da missão. O padrão é `abort()`.
- Reações: `recover(steps)` executa os passos e reentra no passo; `retry()` reentra direto; `abort()` dá TWIST(0, 0) e encerra; `ignore()`; e `ladder(r1, r2, …)`. A escada aplica r_k na k-ésima ocorrência do código no mesmo passo e aborta depois do último degrau (ADR 038).

#### Alvos

- `MapPoint`: vértice em `map`, convertido para `odom` na entrada de cada passo, com o map → odom mais recente (ADR 035).
- `Offset(turn, distance)`: relativo à pose, resolvido uma vez e compartilhado entre passos.
- `heading_to(target)`: rumo da pose atual até o alvo, calculado na entrada.

#### Términos padrão

- TURN_TO: |e_θ| ≤ ε_θ em repouso.
- GO_TO: d ≤ ε_d em repouso.
- Explícitos: `distance_traveled(d)` e `cleared(code)`.
- Giro acima de θ_max é feito em partes. Repouso fora da tolerância gera `NO_PROGRESS` (ADR 036).

Missões de ensaio e a missão por plano usam o mesmo formato e o mesmo motor. Tolerâncias, velocidades e limiares são constantes nomeadas no código do sequenciador.

A pose do robô vem da Odometria. Do TF, o sequenciador só usa o map → odom.

### Callbacks

| Callback | Taxa | Trabalho |
| --- | --- | --- |
| Estado | 100 Hz | Bordas → tabela de reações |
| Odometria | 20 Hz | Pose e predicado do passo |
| Timer | 20 Hz | Republica o comando; verifica a idade do Estado e do heartbeat |
| Resposta do planner | Esporádica | Plano → passos |

Toda transição publica o comando no próprio callback, sem esperar o timer. Ocioso, o sequenciador publica TWIST(0, 0).

### Eventos próprios (ADR 037)

São eventos do próprio sequenciador, que entram na mesma tabela de reações:

| Evento | Condição |
| --- | --- |
| `COMMAND_NOT_ECHOED` | Eco do Estado diferente do comando enviado por mais de T_eco = 0,3 s (T_cmd + 2 períodos de republicação; nota 0006). O comando é comparado ao eco depois de arredondado a float32, o tipo da mensagem |
| `LINK_LOST` | Sem Estado há mais de T_cmd |
| `HEARTBEAT_LOST` | Sem `/heartbeat` do notebook há mais de T_HB = 0,5 s. Por nível; a parada remota é dar Ctrl-C no notebook |
| `BATTERY_LOW` | Tensão abaixo de V_WARN, com histerese H. Por nível |
| `NO_PROGRESS` | Repouso fora da tolerância, depois de ter havido movimento no passo (ADR 036) |

A máscara anterior desconhecida vale 0 ao subir o nó, quando o enlace volta e na entrada de cada passo. Assim, toda condição já ativa nesses instantes gera borda. Esses eventos não fazem parte do `robot-interfaces`.

O notebook publica `/heartbeat` (`std_msgs/Empty`, best effort) a 10 Hz com `ros2 topic pub -r 10`. O sequenciador mede a idade pela hora de chegada.

### Missão por plano

1. O objetivo chega por `/goal_pose` (RViz). Um objetivo novo preempta a missão atual.
2. O sequenciador envia `ComputePathToPose` ao `planner_server`, de forma assíncrona. Resposta de meta antiga é descartada (ADR 034).
3. Os vértices são os pontos onde a direção do `Path` muda, com as pontas e os trechos curtos tratados como na ADR 034. Cada trecho vira um par TURN_TO(rumo) → GO_TO(vértice).
4. Diante de obstáculo frontal no GO_TO: espera T_WAIT, depois `replan()` da pose atual, no máximo N_REPLAN vezes por missão, e por fim aborta (ADR 038).
5. Erro do planner, deliberador ausente, TF ausente, roda travada, bateria baixa ou crítica, heartbeat perdido e enlace perdido abortam a missão.

As missões de ensaio (V-01, V-07, V-08) são escolhidas pelo parâmetro `mission` no launch e começam quando o nó sobe; reiniciar o ensaio é reiniciar o nó. Elas ignoram o `/goal_pose` e o heartbeat. Com `mission` vazio, o nó espera o `/goal_pose`.

## Deliberador (RPi 5)

| Nó | Papel |
| --- | --- |
| `planner_server` (Theta*) | Responde `ComputePathToPose` (ADRs 014 e 034) |
| `slam_toolbox` | Mapeamento contínuo; publica `/map` e map → odom (ADR 040) |
| `ldlidar_stl_ros2` | LDROBOT LD19 (kit D300); publica `/scan` a 10 Hz |
| `static_transform_publisher` | base_link → laser |
| `lifecycle_manager` | Ativa os nós gerenciados |

Não há `bt_navigator` nem `controller_server`: seguir caminho é papel do controlador (ADR 015).

#### Costmap global (ADRs 041 e 042)

- Três camadas: estática (mapa do SLAM), obstáculo (`/scan`, marca e limpa a cada varredura) e inflação. Resolução de 0,05 m.
- Zona proibida = raio do robô + margem m + uma célula. O custo de travessia tem peso mínimo, então o caminho é o mais curto fora da zona proibida.
- O planner pode atravessar espaço desconhecido.
- O VL53L0X fica fora do costmap. Um obstáculo visto só por ele leva a escada ao aborto.

**Launch:** pacote `robot_bringup`, com um processo por nó. Desligar o deliberador (RF-05) é não lançá-lo. O `odom_to_tf_ros2` sobe com o deliberador, o único que consome o odom → base_link. Nos ensaios, o deliberador sobe pelo launch de ensaio: o `deliberator_test.launch.py` na V-04, e na V-08 C1 o mesmo mais o SLAM como carga. O agente e o sequenciador sobem pelos scripts de verificação (`run_vNN`). O launch de operação (`robot.launch.py`) sobe tudo: o agente, o sequenciador e o deliberador na configuração de operação. Ele não é usado nos ensaios e é a fonte do `rqt_graph` da V-09:

| Configuração | Mapa do planner | Costmap global | map → odom | SLAM |
| --- | --- | --- | --- | --- |
| Operação | Do SLAM | Estática, obstáculo e inflação (ADR 041) | SLAM | Ativo |
| Ensaio (V-04, V-08 C1) | M, pelo `map_server` | Estática (M) e inflação, sem `/scan` | Identidade, estático (ADR 035) | V-04: desligado. V-08 C1: frame e tópico próprios, só como carga |

Na V-08 C1, as consultas partem de p₀, informado pela missão de ensaio (ADR 040). Nos ensaios, o costmap não tem camada de obstáculo: com as rodas suspensas a odometria anda e o robô não, e o `/scan` marcaria a sala real em posições erradas sobre o M.

## Implantação no RPi 5

| Processo | Escalonamento |
| --- | --- |
| Agente micro-ROS, sequenciador | SCHED_FIFO 50 (`chrt -f 50`), kernel padrão, sem afinidade (ADR 039) |
| Deliberador, `odom_to_tf_ros2`, driver do LiDAR | Escalonador comum |

O `chrt` roda sem root: o usuário tem `rtprio 50` num arquivo em `/etc/security/limits.d/`, aplicado pelo `pam_limits` a cada sessão ssh. O `chrt -f 50` é prefixo nos scripts de verificação (`MicroRosAgent` do `link.py` e sequenciador dos `run_vNN`) e no launch de operação.

Todos os processos ROS do RPi, inclusive o agente e os scripts de verificação, rodam com `FASTDDS_BUILTIN_TRANSPORTS=UDPv4` (ADR 045). Os scripts de bancada rodam com `env -i`, então a variável é passada explicitamente.

## Descrito, não implementado

O código da tag não tem os itens abaixo. Nenhuma verificação os exercita.

- Bateria (ADR 022, issue #45): a leitura da tensão, o reflexo de bateria crítica e o aborto por bateria baixa.
- Escada da ADR 038: `ladder`, `retry()` e `replan()`, com T_WAIT e N_REPLAN. Sem ela, um obstáculo frontal ou a
  falha do sensor frontal no GO_TO abortam a missão por plano.

## Parâmetros em aberto

Têm ponto de partida, mas o valor final depende de medição:

| Grupo | Parâmetros |
| --- | --- |
| Controlador | a_acel, a_dec, t_s, T_f, S_MIN_VLX = 0,02 MCPS/SPAD e offset do VL53L0X, constante do filtro da bateria, V_WARN, H, prazo do watchdog, deriva entre os relógios |
| Sequenciador | θ_max = 170°, T_HB = 0,5 s, T_eco = 0,3 s |
| Deliberador | Margem do plano m = 0,10 m |
| No chão (issue #27) | d_stop = 0,15 m, v_max |
| Geometria (issue #25) | Raio do robô, pose do LiDAR |

As pendências estão nas issues do robot-docs.
