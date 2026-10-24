# Arquitetura

## Controlador

### Atuação

A referência efetiva passa por uma rampa assimétrica antes do PI (ADR 023).

- a_acel: limitada pela corrente da bateria.
- a_dec: mais íngreme, limitada pelo escorregamento e por não aplicar tensão reversa com a roda girando.

O integrador só acumula fora da saturação (duty ≤ 48 %).
O DRV8871 opera em decaimento lento; a frenagem é o próprio PWM, e o freio total é duty = 0.

"Duty" é a fração de acionamento d (fração do período em 1-0 ou 0-1); o restante do período é freio (1-1).
d ≤ 48 % limita a tensão média no motor a ≈ 6 V. d = 0 é freio total.

A frequência do PWM deve ser alta em relação a L/R do motor (ordem de 20 kHz).
v_max deve ser alcançável com a bateria em até V_CRIT.
v_max e D_STOP obedecem d_parada(v_max) + v_max·T_S ≤ D_STOP ≤ d_sensor, com d_parada ≈ v_max²/(2·a_dec) + latências (ADRs 021 e 023).
Os valores saem do ensaio de d_stop da V-03.

### Troca de dados entre contextos do controlador

ISR do encoder, tarefa de controle, tarefa de sensor e tarefa micro-ROS trocam dados só por caixas de correio do FreeRTOS (ADR 017).
São quatro caixas:

- comando: micro-ROS -> controle;
- estado: controle -> micro-ROS;
- bordas do encoder: ISR -> controle;
- sensor frontal: sensor -> controle (ADR 020).

Cada uma guarda o último valor e tem um único produtor.
A tarefa de controle nunca espera por elas (RNF-01).

### Componentes do firmware

O firmware se divide em dois componentes ESP-IDF (ADR 018):

- `controlador`: tarefa de tempo real, sensores, atuação e caixas de correio.
- `enlace`: tarefa micro-ROS e conversão de mensagens.

O `enlace` depende do `controlador`, nunca o contrário.
O `main` apenas inicializa os dois.

### Encoders

A ISR de captura registra apenas o instante e a contagem acumulada de bordas de cada roda.
A tarefa de controle calcula a partir desses registros:

- o período;
- a velocidade, nula após T_VEL sem borda;
- o sentido;
- a odometria.

O sentido de cada roda fica travado enquanto ela gira.
Só é reavaliado com a roda parada, quando passa a seguir a tensão aplicada (ADR 019).

### Tarefas do controlador

| Tarefa | Núcleo | Tempo real | Função |
| --- | --- | --- | --- |
| Controle | 1 | Sim (T_C = 10 ms) | Ciclo de controle |
| Sensor | 0 | Não | Lê o VL53L0X no ritmo do sensor (ADR 020) |
| micro-ROS | 0 | Não | Enlace com o sequenciador |

A tarefa de sensor publica distância, status e instante da medida numa caixa de correio.
A tarefa de controle a lê sem esperar (ADR 017).
A prioridade é decrescente na ordem da tabela.

### Reflexos do controlador

Reflexo é a resposta local do controlador a uma condição que ele próprio detecta.
Exemplos: obstáculo, bateria crítica, falha de sensor, erro interno.
Todo reflexo segue duas regras:

- só restringe a referência recebida, nunca a amplia;
- é reportado ao sequenciador, que decide a recuperação (RF-02, RF-03).

#### Reflexo de obstáculo frontal

A cada ciclo, a tarefa de controle classifica a leitura do VL53L0X em um de três estados:

- obstáculo;
- livre;
- falha: sem leitura classificável há mais de T_S.

Obstáculo e falha zeram o avanço da referência; giro e ré continuam permitidos (ADR 021).
A recuperação do barramento fica na tarefa de sensor.

#### Reflexo de bateria crítica

A tarefa de controle lê o ADC da bateria a cada ciclo e mantém a tensão filtrada.
Abaixo de V_CRIT, a referência vai a zero.
O reflexo libera sozinho quando a tensão volta acima de V_CRIT, sem retenção nem histerese (ADR 022).
Cada episódio é reportado ao sequenciador, que é dono do limiar de aviso e da decisão de encerrar a missão.

### Comportamentos primitivos

O controlador tem três comportamentos, selecionados pelo sequenciador por uma mensagem própria
que traz o comportamento ativo e seus parâmetros (ADR 024):

| Comportamento | Controla | Parâmetros |
| --- | --- | --- |
| TWIST | Velocidade linear e angular | (v, ω) |
| TURN_TO | Posição angular | θ (odom) |
| GO_TO | Posição linear | (x, y) (odom) |

Cada comportamento produz uma referência (v, ω).
Essa referência passa pelos reflexos, pelo vencimento e pela rampa antes do PI,
então uma troca de comportamento nunca é brusca nos motores.

O controlador nunca decide término nem troca de comportamento; isso é papel do sequenciador.
Os estados TURN_TO -> GO_TO do sequenciador correspondem aos comportamentos de mesmo nome (ADR 015, ADR 024).

### Interface do controlador com o RPi

| Sentido | Tópico | Tipo | Taxa |
| --- | --- | --- | --- |
| RPi -> ESP32 | Comando | Próprio (comportamento + parâmetros) | 20 Hz |
| ESP32 -> RPi | Estado | Próprio (falhas e reflexos ativos em máscaras de 64 bits, eco do comando: comportamento ativo e parâmetros em vigor) | 100 Hz |
| ESP32 -> RPi | Odometria | Odometry | 20 Hz |
| ESP32 -> RPi | Bateria | BatteryState | ~1 Hz |
| ESP32 -> RPi | Instrumentação | Próprio (C_max, R_max, prazos perdidos; Δ e índice do evento da V-07) | 10 Hz |

Todos com QoS best effort, volatile, profundidade 1 (ADR 025).
Ocupação do enlace ≈ 20 % (orçamento: 50 %).
Dados novos seguem o critério da ADR 025.

### TF odom -> base_link

O pacote `odom_to_tf_ros2`, no RPi, assina a odometria e transmite o TF odom -> base_link com o carimbo original da mensagem (ADR 026).

### TF e tempo

O controlador registra o instante de cada pose no relógio local do ESP32.
A tarefa micro-ROS sincroniza periodicamente esse relógio com o do agente e converte o instante ao publicar.
A odometria só é publicada após a primeira sincronização (ADR 027).

### Ciclo da tarefa de controle

A cada T_C = 10 ms, liberado nos instantes t_k:

1. Ler as caixas de correio: comando, bordas do encoder, sensor frontal (ADR 017).
2. Medir: velocidade e sentido das rodas, odometria, tensão filtrada da bateria (ADR 019).
3. Calcular a referência (v, ω) pelo comportamento ativo (ADR 024).
4. Restringir: vencimento do comando e reflexos, gerando a referência efetiva (RNF-02, ADRs 021 e 022).
5. Aplicar a rampa assimétrica (ADR 023).
6. Converter pela cinemática inversa na referência de cada roda.
7. PI por roda, com integração condicional e saturação d ≤ 48 % (ADR 023).
8. Escrever o PWM.
9. Monitor de falha (RF-02).
10. Publicar o estado e a instrumentação (ADRs 025 e 027).

A atuação (até a etapa 8) vem antes da manutenção (etapas 9 e 10),
o que mantém mínimo e constante o atraso entre medida e PWM.
As restrições da etapa 4 comutam entre si.

### Estado interno do controlador

- Filtragem: tensão filtrada da bateria, velocidade e sentido de rotação de cada roda (ADR 019), pose da odometria e integrador do PI, limitado pela integração condicional e zerado na zona morta (ADRs 023 e 030).
- Efêmero: comando, que vence por idade (ADR 017, RNF-02); sensor frontal, que envelhece até a falha (ADR 021); códigos de prazo perdido e de reinício por watchdog, ativos por tempo limitado (ADRs 028 e 029).
- Fora do escopo: a instrumentação, que é ferramenta de verificação e não existe no build de produção (ADR 028).

### Inicialização e watchdog

O boot é seguro por construção:

- drivers em roda livre pelos pull-downs internos do DRV8871 (ADR 008);
- caixa de comando vazia = comando vencido (ADR 017);
- sensor frontal em falha até a primeira leitura válida (ADR 021);
- odometria só após a primeira sincronização (ADR 027).

A tarefa de controle é vigiada pelo watchdog de tarefas do ESP-IDF, com prazo de poucos T_C (ADR 029).
Após um reinício por watchdog, o estado publica o código "reinício por watchdog" por tempo limitado.

Cada camada vigia a de cima:

- o watchdog do ESP-IDF vigia a tarefa de controle;
- o controlador vigia o sequenciador pelo vencimento do comando;
- o sequenciador vigia o notebook pelo heartbeat (ADR 016).

### Instrumentação e prazo perdido

A instrumentação (C_max, R_max, prazos perdidos) é ferramenta de verificação, ativada por opção de build (ADR 028).

- Build de verificação: mede no `controlador`, acumula desde o boot e publica pelo `enlace`.
- Build de produção: a instrumentação não existe no binário.

A perda de prazo é detectada em todos os builds.
Ela aparece como código de falha no estado, ativo por tempo limitado, sem reflexo.

## Sequenciador

### Processo

O sequenciador é um único nó ROS 2 em Python (rclpy), num único processo (ADR 031).
O nó concentra:

- a execução dos passos;
- a republicação do comando;
- a detecção de bordas;
- o heartbeat;
- o aviso de bateria;
- a consulta ao deliberador.

### Estrutura

Uma missão é uma lista de passos: comportamento, parâmetros calculados na entrada e predicado de término (ADR 032).
O predicado satisfeito avança ao próximo passo.
Uma borda de subida nas máscaras do Estado consulta a tabela de reações pelo código: insere passos de recuperação, aborta ou ignora.
Missões de ensaio e a missão do plano usam o mesmo formato.

| Peça | O que é |
| --- | --- |
| `Mission(steps, reactions)` | Lista de passos e tabela padrão de reações |
| `Step(behavior, until, reactions)` | Comportamento, término opcional e reações próprias |
| Comportamentos | `TWIST(v, ω)`, `TURN_TO(θ)`, `GO_TO(target)` (ADR 024) |
| Alvos | `MapPoint`: reconvertido a cada entrada (ADR 035). `Offset(turn, distance)`: resolvido uma vez e compartilhado entre passos |
| `heading_to(target)` | Rumo da pose atual até o alvo, calculado na entrada |
| Términos (`until`) | Padrão do TURN_TO: \|e_θ\| ≤ ε_θ em repouso. Padrão do GO_TO: d ≤ ε_d em repouso. Explícitos: `distance_traveled(d)`, `cleared(code)` |
| Reações | `recover(steps)`: executa os passos de recuperação e reentra no passo. `retry()`: reentra direto. `abort()`: TWIST(0, 0) e fim. `ignore()`: o código não afeta o passo |

Bordas só disparam reações; términos testam condições atuais.
A reação é escolhida por código ou grupo de códigos, do passo para a missão, com `abort()` como padrão.
Tolerâncias e velocidades são parâmetros ROS.

Giro acima de θ_max é feito em duas partes, por reentrada no TURN_TO.
Repouso fora da tolerância, depois de movimento no passo, gera o evento `NO_PROGRESS` para a tabela de reações (ADR 036).

### Eventos

- Só bordas de subida das máscaras do Estado disparam reações (ADR 037).
- Máscara anterior desconhecida vale 0: toda condição ativa ao subir o nó, quando o enlace volta ou na entrada de um passo gera borda.
- Eco diferente do último comando enviado por mais de T_eco (> T_cmd) gera `COMMAND_NOT_ECHOED`.
- Sem Estado há mais de T_LINK = T_cmd gera `LINK_LOST`, verificado no timer de republicação.
- Sem heartbeat há mais de T_HB, a condição `HEARTBEAT_LOST` fica ativa (por nível).
- Tensão do BatteryState abaixo de V_WARN ativa `BATTERY_LOW`, que só cai acima de V_WARN + H (histerese, ADRs 009 e 022).
- Eventos do próprio sequenciador (`NO_PROGRESS`, `COMMAND_NOT_ECHOED`, `LINK_LOST`, `HEARTBEAT_LOST`, `BATTERY_LOW`) entram na mesma tabela de reações e não fazem parte do `robot-interfaces`.

### Recuperação

A reação pode ser uma escada, `ladder(r1, r2, …)`: a k-ésima ocorrência do código no mesmo passo aplica r_k, e depois do último degrau vem `abort()` (ADR 038).
Esperas usam `wait_until_clear(code, timeout)`, que ignora o próprio código; o tempo estourado sobe um degrau.
`replan()` pede um plano novo da pose atual, no máximo N_REPLAN vezes por missão.
A tabela da missão por plano está na ADR 038.

### Heartbeat

O notebook publica `/heartbeat` (`std_msgs/Empty`, best effort) a 10 Hz, com `ros2 topic pub -r 10`; Ctrl-C é a parada remota (ADR 016).
O sequenciador mede a idade pela hora de chegada; acima de T_HB = 0,5 s, `HEARTBEAT_LOST` aborta a missão com TWIST(0, 0) explícito (ADR 038).
O heartbeat é exigido por padrão; as missões de ensaio (V-01, V-07, V-08) o ignoram na tabela e rodam sem notebook.

### Execução

| Callback | Taxa | Trabalho |
| --- | --- | --- |
| Estado | 100 Hz | Bordas nas máscaras -> tabela de reações |
| Odometria | 20 Hz | Pose e predicado do passo |
| Timer | 20 Hz | Republica o comando vigente (RNF-02) |
| Resposta do deliberador | Esporádica | Plano -> passos |

Todos os callbacks rodam num executor de uma thread (ADR 033).
A consulta ao deliberador é assíncrona; o planejamento roda em outro processo.
Toda transição publica o comando no próprio callback, sem esperar o timer.
Ocioso (sem missão ou depois de `abort()`), o sequenciador continua publicando TWIST(0, 0) a 20 Hz.

### Consulta ao deliberador

O sequenciador pede o plano ao `planner_server` do Nav2 pela action `ComputePathToPose`, sem bloquear (ADRs 014 e 033).
O planner é o Theta*: o caminho é uma poligonal interpolada na resolução do mapa.
O sequenciador extrai os vértices onde a direção muda e gera um par TURN_TO -> GO_TO por trecho (ADR 034).
Resposta de meta antiga é descartada; erro do planner ou deliberador ausente é falha da missão.

### Conversão map -> odom

Na entrada de cada passo, o vértice é convertido de `map` para `odom` com o TF mais recente; o alvo fica fixo durante o passo (ADR 035).
O TF é lido por um buffer do `tf2_ros` no executor do nó, sem espera.
A pose do robô vem da Odometria; do TF só se usa o map -> odom, publicado pelo SLAM.
Com as rodas suspensas (V-04), o launch publica map -> odom estático e identidade.

### Missões

- Missão por plano: o objetivo chega por `/goal_pose` (PoseStamped), publicado pelo "2D Goal Pose" do RViz. Um objetivo novo preempta a missão atual.
- Missões de ensaio (V-01, V-07, V-08): escolhidas pelo parâmetro `missao` no launch e iniciadas quando o nó sobe. Reiniciar o ensaio é reiniciar o nó.
- Com `missao` vazio, o nó espera `/goal_pose`; com uma missão de ensaio, ignora `/goal_pose`.

### Implantação

O agente micro-ROS e o sequenciador rodam em SCHED_FIFO, prioridade 50 (`chrt -f 50`), no kernel padrão, sem afinidade de núcleo (ADR 039).
O deliberador (Nav2, SLAM) e o `odom_to_tf_ros2` ficam no escalonador comum.

## Deliberador

### Nós

| Nó | Função |
| --- | --- |
| `planner_server` (Nav2, Theta*) | Responde `ComputePathToPose` ao sequenciador (ADRs 014 e 034) |
| `slam_toolbox` | Mapeia continuamente; publica o mapa e map -> odom (ADR 040) |
| `ldlidar_stl_ros2` | Driver do LiDAR (LDROBOT D500); publica `/scan` a 10 Hz |
| `static_transform_publisher` | base_link -> laser |
| `lifecycle_manager` | Configura e ativa os nós gerenciados |

Sem `bt_navigator` nem `controller_server` (ADR 015).

### Costmap global

Três camadas: estática (mapa do SLAM), obstáculo (`/scan`) e inflação, na resolução do mapa, 0,05 m (ADR 041).
O VL53L0X fica fora: um obstáculo visto só por ele termina a escada em aborto (ADR 038).
A zona proibida do planner é raio do robô + margem m, e o custo de travessia tem peso mínimo (ADR 042).
O planner pode atravessar espaço desconhecido.

### Árvore de frames

map -> odom (SLAM, ADR 040) -> base_link (`odom_to_tf_ros2`, ADR 026) -> laser (estático).

### Launch

O deliberador tem launch próprio, separado do do sequenciador, com um processo por nó.
Desligar o deliberador (RF-05, V-01) é não lançá-lo, e ele fica no escalonador comum (ADR 039).
Um argumento escolhe a configuração:

- operação: SLAM publica o mapa e map -> odom; o planner usa o mapa do SLAM;
- ensaio (V-04, V-08 C1): `map_server` serve o M e o launch publica map -> odom identidade (ADR 035); na V-08 C1, o SLAM roda com frame e tópico próprios, só como carga (ADR 040).
