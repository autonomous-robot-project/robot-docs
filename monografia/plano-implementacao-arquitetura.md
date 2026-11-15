# Plano da seção "Implementação da Arquitetura" (Cap. 3)

Aprovado pelo Lucas em 15/11/2026. Substitui o esboço em laranja de `capitulos/3-materiais-e-metodos.tex`
(seção `Sec:implementacao` e subseções), que é apagado no início da primeira sessão de escrita.

## Nível de abstração (nível C)

Um item entra no texto só se for:

1. a alocação de uma camada num processador ou contexto;
2. o mecanismo que atende um RF ou RNF;
3. um conceito que um Teste do Cap. 3 ou uma Folha usa.

Fica fora:

- o ciclo passo a passo;
- a amostragem do encoder;
- os pinos (os do ensaio estão nas Folhas);
- o PWM;
- o boot dos drivers;
- a bateria e a escada de recuperação (ADRs 022 e 038, não implementadas): uma frase nos Trabalhos Futuros;
- a operação com SLAM no chão;
- a separação domínio/infraestrutura: no máximo uma frase.

Uma divergência entre documentação e código só se corrige se entra no texto nesse nível. Emendas de ADR só se as ADRs
forem para apêndice (decisão do Lucas com a orientadora).

## Princípios de redação

- **Ordem de leitura.** A leitura sobe pelas camadas, na ordem dos requisitos.
  - Cada parte abre pelo requisito que motiva o mecanismo e explica o mecanismo.
  - Ela fecha com a alternativa rejeitada, quando isso ajuda a defender a escolha.
- **Figuras.** A seção abre com uma figura simples da implantação. Ela fecha com a mesma figura detalhada e marcada
  com os requisitos. O fechamento mostra a alocação segundo os requisitos, sem dizer "objetivo específico".
- **Símbolos.** O leitor não vê o código.
  - Texto corrido, sem símbolos e com os valores numéricos.
  - Símbolo só em equação ou figura, definido na primeira menção, com a grafia dos Testes (T_sens, não T_S).
- **Nomes.** Sem nomes de variáveis, classes ou arquivos. Ficam só `vTaskDelayUntil`, `xTaskCreatePinnedToCore`
  e os nomes que os Testes já usam: os tópicos (Command, State, Odometry, Instrumentation), `planner_server`,
  `compute_path_to_pose` e `odom_to_tf`.
- **Floats.** Todo float tem antes um parágrafo que resume o conteúdo dele.
  - Especificador [htb], legenda acima e `\fonte{Autoria própria (\imprimirano).}`.
- **Remissões.** Sem "Seção X" e sem "a coluna".
- **Requisitos no parágrafo.** O código do requisito vem com o nome ("o vencimento do comando (RNF-02)").
- **Estilo.** Sem advérbios não técnicos. Sem dois-pontos nem ponto e vírgula no meio do parágrafo. Sem "bastar" e
  sem "a cargo de".
- **Citações.**
  - Gat (1998) só onde o texto dele sustenta a frase, conferido na fonte. O argumento é a arquitetura do Lucas.
  - ADRs não são citadas pelo número. O robot-docs pode ser mencionado como rascunho das decisões.
- **Marcação.** Texto novo em laranja (`[HTML]{BF5700}`). Referências fora do ref.bib em vermelho.
- **Versão.** O código ensaiado é a tag v1.0.0 (robot-firmware 16ce5dd, robot-ros-system 8ad2968). A v1.0.1 só
  muda nomes e comentários.

## Estrutura

### Abertura (sem subtítulo)

1. **Ponte.** Os requisitos não fixam a plataforma. O determinismo do laço (RNF-01) levou o controlador a um
   microcontrolador dedicado. A escolha do hardware fixou o ESP32-S3 e o Raspberry Pi 5. A abertura diz como as
   camadas são implantadas neles e como se comunicam.
2. **Alocação e enlace.**
   - O controlador roda sobre FreeRTOS no ESP32-S3. O sequenciador e o deliberador rodam como processos ROS 2 no RPi.
   - O enlace é micro-ROS sobre UART direta a 921 600 baud. Explicar o micro-ROS e o agente no RPi.
   - Alternativas rejeitadas: protocolo próprio com nó-ponte (ADR 012) e USB (ADR 043).
   - **Figura 1, implantação.** Os dois processadores, as camadas em cada um, o agente e o enlace.
3. **Tabela de tecnologias e versões.** Tecnologia, versão, camada e finalidade.
   - Conteúdo: ESP-IDF 5.2.6, micro-ROS 24.0.0, ROS 2 Jazzy, Nav2, slam_toolbox, `ldlidar_stl_ros2` v3.0.3 e
     `odom_to_tf_ros2` 1.1.1, mais a tag v1.0.0 com os dois repositórios.
   - Absorve a antiga "Ferramentas e Tecnologias", que é removida na sessão da abertura do Cap. 3.

### Controlador

1. **Tarefas e núcleos (RNF-01).**
   - A tarefa de controle tem a maior prioridade e é a única do projeto no núcleo 1.
   - A tarefa do sensor frontal fica no núcleo 0. A leitura do VL53L0X leva de 20 a 33 ms e uma transação I²C pode
     bloquear (ADR 020). Alternativa rejeitada: ler o sensor no ciclo.
   - A micro-ROS e as interrupções também ficam no núcleo 0.
   - O firmware tem duas partes, e o controle não depende da comunicação (ADR 018).
2. **Troca de dados.** Fila de um elemento sobrescrita, e o leitor nunca espera (ADR 017).
   - **Figura 2, tarefas e canais.** Núcleos, tarefas com prioridade, canais e periféricos.
3. **Ciclo de controle (RNF-01).**
   - Roda a cada 10 ms por `vTaskDelayUntil`, na sequência mede, calcula a referência, restringe, atua, supervisiona
     e publica.
   - A atuação vem antes da manutenção, para manter constante o atraso entre medida e PWM.
   - Sem E/S, sem alocação e sem laço sem limite.
   - Medição de tempo de execução e de prazos perdidos sempre presente (ADR 028, Teste 5).
   - O watchdog de tarefas reinicia o ESP32 com 30 ms (três períodos) sem cumprir o período (ADR 029, RF-02).
4. **Comportamentos (RF-01, RNF-04).**
   - Tabela: comportamento, parâmetros, o que faz.
   - Equações do GO_TO e do TURN_TO com cada símbolo definido.
     - O perfil usa 90 % da desaceleração, como em `A_DEC_PROFILE = 0,9·A_DEC` no código. Isso difere da ADR 030,
       e vale o código ensaiado.
   - Continuidade: o GO_TO tende a (0, 0) junto do alvo. A descontinuidade do TURN_TO em 180° é evitada pelo
     sequenciador.
   - Rampa assimétrica (0,25 m/s² na aceleração, 0,5 m/s² na desaceleração) em toda troca (ADR 023).
   - Um parágrafo sobre o PI por roda, com zona morta abaixo de 0,07 m/s e ganhos do modelo do motor (D2).
5. **Reflexo e falhas (RF-02, RF-03).**
   - Tabela de condições reportadas, com detecção, efeito no comando e duração:
     - obstáculo frontal;
     - falha do sensor;
     - falha cognizante;
     - prazo perdido;
     - reinício por watchdog;
     - falha de ensaio.
   - A falha do sensor restringe como obstáculo, com giro e ré livres. Alternativa rejeitada: parada total (ADR 021).
6. **Estado efêmero (RNF-02).**
   - O comando vence em 200 ms e vira parada. Com a republicação a 20 Hz, isso exige quatro comandos seguidos perdidos.
   - Justificar a "ausência de decisão" frente ao RNF-04: sem comando válido, resta o comportamento padrão, que não usa
     modelo do mundo.
   - A velocidade vale zero sem pulso por 0,3 s. A pose e o sentido travado (ADR 019) são filtragem.

### Interface entre o Controlador e o Sequenciador

1. **Tabela de tópicos.** Tópico, sentido, tipo, taxa e conteúdo.
   - Mensagem própria só onde nenhum tipo padrão carrega comportamento com parâmetros.
   - Alternativa rejeitada: Twist com tópico de modo separado, não atômico (ADR 024).
2. **Condições como estado atual (ADR 025).** O State repete as condições a cada 10 ms e o sequenciador detecta as
   bordas. Uma mensagem perdida não perde o evento.
3. **Eco do comando.** Confirmação de recebimento.
4. **Uma frase cada:**
   - QoS best effort, profundidade 1;
   - ocupação do enlace de cerca de 20 %, a conferir na fonte;
   - carimbo da odometria no relógio sincronizado (ADR 027).

### Sequenciador

1. **Nó e execução (RNF-03).**
   - Nó Python com executor de uma thread, que executa um callback por vez.
   - A transição publica no próprio callback.
   - Alternativas rejeitadas: C++, com 2 a 3 vezes mais código e só se o Teste 7 reprovasse; executor multithread,
     sem paralelismo pelo GIL (ADRs 031 e 033).
2. **Missão (RF-04).**
   - Uma sequência de passos. Cada passo tem comportamento, término e reações, e os parâmetros são calculados na
     entrada a partir da pose (ADR 032).
   - **Figura 3, ciclo de vida de um passo.**
   - Reações: abortar, ignorar e recuperar. A tabela do passo é consultada antes da da missão, e o padrão é abortar.
3. **Términos (RNF-04, ADR 036).**
   - TURN_TO: até 10° de erro, em repouso.
   - GO_TO: até 0,05 m, em repouso.
   - Giro acima de 170° feito em partes.
   - Sem progresso por 1 s gera evento.
4. **Tabela de eventos próprios (ADR 037).**
   - Comando não ecoado: 0,3 s.
   - Enlace perdido: 0,2 s.
   - Heartbeat perdido: 0,5 s. Explicar a parada remota pelo notebook a 10 Hz.
   - Sem progresso.
   - Máscara anterior 0 na entrada do passo, para que toda condição já ativa gere borda.
5. **Vigilância em cadeia.**
   - O watchdog vigia a tarefa de controle.
   - O vencimento vigia o sequenciador.
   - O heartbeat vigia o operador.

### Deliberador

1. **Planejamento por consulta (RF-05, RF-06; ADRs 014, 015, 034).**
   - O `planner_server` responde à action, que é uma requisição com resposta assíncrona.
   - O Theta* gera caminhos em segmentos retos, com poucos vértices.
   - Sem `controller_server`: seguir o caminho é laço entre sensor e atuador, papel do controlador.
2. **Mapa de custo (ADRs 041 e 042).**
   - Zona proibida igual a raio + 0,10 m + uma célula. Com o custo de travessia mínimo, o caminho é o mais curto fora
     dela.
   - Tabela operação × ensaio:
     - operação: SLAM contínuo;
     - ensaios: mapa M e map → odom identidade, sem a camada de obstáculo porque as rodas ficam suspensas;
     - Teste 8: SLAM só como carga.
3. **Integração (RF-07; ADRs 034 e 035).**
   - **Figura 4, do objetivo ao comando.** Objetivo, consulta, plano, vértices, pares TURN_TO → GO_TO, conversão
     map → odom na entrada do passo e o Command.
   - Por que converter na entrada do passo: converter tudo no início perde a correção do SLAM, e reconverter a cada
     republicação move o alvo.
   - O objetivo novo preempta a missão e a resposta antiga é descartada. A consulta e o TF não bloqueiam.

### Isolamento no Computador Embarcado (RNF-05)

- O agente e o sequenciador rodam em SCHED_FIFO 50 (explicar), e o deliberador no escalonador comum, com kernel
  padrão (ADR 039).
- Fast DDS só com UDP (ADR 045): é contorno de um defeito de biblioteca e nenhum Teste o cita. No máximo uma oração,
  sem estatística.
- O controlador está isolado por estar em outro processador.

### Generalização e fechamento

1. **Tabela de recursos e equivalentes.** Pedido da orientadora. Partir da tabela do esboço e acrescentar micro-ROS
   e UART, tópicos e actions, e Nav2.
2. **Figura 5, implantação com os requisitos.** A Figura 1 detalhada, com cada mecanismo marcado com o RF ou RNF que
   atende: tarefa, canal, nó, tópico, prioridade.
   - O parágrafo de fechamento diz que todo requisito tem mecanismo num processador e num contexto, e que as
     restrições de tempo ficam nos contextos dedicados ou de maior prioridade.
   - Ele retoma as invariantes (D3) e faz a ponte com o planejamento dos testes (requisito → teste).

## Decisões (15/11)

| # | Decisão |
| --- | --- |
| D1 | O fechamento é a Figura 5, implantação marcada com os requisitos |
| D2 | Um parágrafo sobre o PI aqui. A caracterização dos motores e do encoder vai para a Escolha do Hardware |
| D3 | Invariantes diluídas no texto, cada uma onde o mecanismo aparece, e retomadas no parágrafo da Figura 5 |
| D4 | Bateria e escada ficam fora, com uma frase nos Trabalhos Futuros |
| D5 | Este plano em markdown próprio. O esboço do .tex é apagado no início da escrita |

## Contrato com a seção "Escolha do Hardware para a Validação"

A Escolha do Hardware vem antes no texto e é escrita depois desta seção. A Implementação parte destes fatos sem
repeti-los, então a Escolha do Hardware precisa apresentá-los:

1. **Alocação no nível dos processadores.** O RNF-01 leva o controlador a um microcontrolador dedicado. O sequenciador
   e o deliberador ficam no computador embarcado, com Linux e ROS 2. Dizer a alternativa rejeitada (tudo no RPi) e o
   motivo (ADR 002).
2. **ESP32-S3 com dois núcleos.** É a base da separação entre a tarefa de controle e as demais.
3. **Raspberry Pi 5,** com o número de núcleos, que o Teste 8 usa no `stress-ng`.
4. **Tempos dos sensores.**
   - VL53L0X: medida a cada 20 a 33 ms, por I²C.
   - LD19: 10 Hz, que é a origem do T_seq.
5. **Encoder de canal único,** com 10,2 mm por pulso e sem sentido de rotação.
6. **Caracterização (D2).**
   - Ganho K e constante de tempo τ dos motores.
   - Zona morta do PWM e contagem do encoder com amostragem (notas 0010 e 0011).
   - Valores adotados: K = 1,3 e τ = 0,04 s.
7. **Enlace físico.** UART direta pelos GPIO, alimentação do ESP32 pela USB do RPi.

Se a escrita do Hardware mudar algum desses fatos, a Implementação é revista no ponto afetado.

## Sessões de escrita

Divididas por repositório, para que cada sessão carregue o contexto de uma base de código só:

1. **Firmware.** Primeiro `git pull overleaf` e apagar o esboço. Depois a abertura, a Tabela de tecnologias, o
   Controlador e a Interface.
   - Conferir no firmware e nas notas: o perfil 0,9·a_dec, as tarefas, o watchdog e a ocupação do enlace.
2. **ROS.** O Sequenciador, o Deliberador, o Isolamento, a Generalização e a Figura 5.
   - Conferir no robot-ros-system e nas ADRs 039 e 045: 330 ms e 7/60.
3. **Revisão.** Uma rodada, que pode ser no fim da sessão 2 se o contexto permitir. Depois tirar o laranja, commitar,
   e fazer push para overleaf e github.

As figuras são TikZ dentro do .tex, como no resto da monografia.

## Estado (15/11)

- **Sessão 1 feita.** robot-thesis `dedc620`, mais `c4eb38d` sem laranja, já no Overleaf e no GitHub.
  - Abertura com a Figura 4 (implantação), a Tabela 6 (tecnologias) e a Tabela 7 (repositórios).
  - Controlador em cinco subsubseções:
    - Tarefas e Troca de Dados, com a Figura 5;
    - Ciclo de Controle, com a Figura 6;
    - Comportamentos e Controle das Rodas, com as Tabelas 8 e 9 e as Equações 11 e 12;
    - Reflexo e Falhas, com a Tabela 10;
    - Estado Efêmero.
  - Interface entre o Controlador e o Sequenciador, com a Tabela 11.
- **Sessão 2 feita, com a revisão.** robot-thesis `3127ee6`, mais `d9f06d4` sem laranja, já no Overleaf e no GitHub.
  - Sequenciador em três subsubseções: Nó e Execução; Missões e Reações, com a Figura 7; Eventos e Vigilância, com
    a Tabela 12.
  - Deliberador em três subsubseções: Planejamento por Consulta; Mapa de Custos, com a Tabela 13; Integração com o
    Sequenciador, com a Figura 8.
  - Isolamento no Computador Embarcado. Generalização e Síntese, com a Tabela 14 e a Figura 9.
  - `\FloatBarrier` (pacote `placeins`) antes de "Planejamento de Testes".
- **Critérios de Gat (opção B, decisão do Lucas).** Velocidade e estado interno são guias, não os únicos critérios.
  - A abertura dos Requisitos os cita de forma breve.
  - O fechamento da Implementação os aplica sem citar Gat de novo.
  - A Fundamentação os define por completo. O esboço do Cap. 2 tem o item do estado, em laranja.
- **Pendente.** A frase da bateria e da escada nos Trabalhos Futuros (D4). O contrato com a Escolha do Hardware
  continua valendo.
- **Texto da sessão 1 como referência.** Ler o texto já escrito como referência de estilo e de termos antes de
  escrever. Ele já define vários conceitos, que a sessão 2 retoma sem redefinir:
  - canal de último valor;
  - eco do comando;
  - códigos de falha e de reflexo publicados como estado;
  - vencimento em 200 ms, republicação a 20 Hz;
  - "falha da roda";
  - a parada pelas falhas vem do sequenciador.

## Decisões de redação da sessão 1

- **Links.** Endereços (URLs) só em tabela, nunca no texto.
- **Falhas.** "Falha da roda" para o erro de velocidade da roda, o termo da Folha B.9. "Falha cognizante" é o nome do
  RF-02 e vale para todas as falhas reportadas. O código e o arquitetura.md mantêm o nome antigo, mas a monografia
  não cita nomes do código.
- **Resultados de bancada.** O sobressinal do PI (nota 0011) e outros resultados pertencem aos testes, não à
  Implementação, que descreve o projeto.
- **Continuidade.** O RNF-04 trata da saída de cada comportamento em função do seu estado interno, não da transição
  entre comportamentos. A rampa limita a aceleração (corrente na partida) e a desaceleração (escorregamento e frenagem
  sem tensão reversa), e nenhum teste a verifica.
- **Argumentos.** Nenhum argumento que o protótipo de bancada não testou. Exemplo: o sequenciador manobrar para se
  afastar de um obstáculo.
- **Restrição e reação.** No controlador, só o sensor frontal restringe o comando, por obstáculo ou falha do sensor.
  As outras falhas são só reportadas, e a parada vem da reação padrão do sequenciador, que é abortar. A Tabela 10 usa a
  coluna "Restrição no controlador". O Sequenciador traz só o modelo de reações: abortar (o padrão), ignorar e
  recuperar. As exceções de cada missão já estão nas Folhas, e o texto as remete à Folha de cada teste, sem tabela de
  missões e sem justificar exceção que nenhum teste usa.
- **Estrutura.** Subsubseções para dar pausa na leitura. Equações com uma tabela de símbolos, e o texto explica o que
  cada parcela faz.
- **Passos.** Uma figura para os passos de um processo (como o ciclo), com o texto resumido.

## Ajustes da sessão 2 (15/11)

A sessão 2 desceu abaixo do nível C no primeiro plano. Ficou decidido:

- **Estrutura.**
  - Sequenciador com três subsubseções: Nó e Execução; Missões e Reações (Figura 7, ciclo de vida do passo); Eventos e
    Vigilância (tabela de eventos e a vigilância em cadeia num parágrafo).
  - Deliberador sem subsubseções, com a tabela operação × ensaio e a Figura 8.
  - Isolamento no Computador Embarcado em um parágrafo.
  - Generalização e Síntese com a tabela de recursos e a Figura 9.
- **Alternativa ao Python.** Uma frase, sem o número "2 a 3 vezes mais código", com a migração condicionada ao Teste 7.
- **Tabela de recursos.** As cinco linhas do esboço mais canal de último valor, micro-ROS sobre UART, tópicos e
  action, e Nav2 com o SLAM.
- **Gat.** Só na consulta assíncrona ("several Behavior transitions can occur between the time a deliberative
  algorithm is invoked and the time it produces a result").
- **Sem issues nem emendas novas.** O arquitetura.md já marca escada e bateria em "Descrito, não implementado". As
  divergências ADR 045 × nota 0007 e ADR 034 × código ficam fora do texto, conforme a triagem.

## Lições técnicas da sessão 1

- **Edição.** O Lucas edita o .tex à mão entre as rodadas.
  - Só trocas pontuais, conferindo antes que o trecho a trocar existe (`assert` da contagem).
  - Nunca reescrever um bloco inteiro.
  - Antes de remover o laranja ou de commitar, conferir o `git diff` para não perder as edições dele.
- **TikZ.**
  - O preâmbulo carrega `positioning`, `arrows.meta` e `fit`. Bibliotecas novas podem ser acrescentadas.
  - Não usar `step` como nome de estilo, porque é chave do TikZ (usar `cstep`).
  - Conferir cada figura renderizada (`pdftoppm`) antes de mostrar.
- **Identificador longo** em `\texttt` que passa da margem: `sloppypar` no parágrafo, ou `\allowbreak` depois de uma
  barra.
- **Compilação.** Se o latexmk sair com código 12 e erro em `\BKM@entry`, os `.aux` corromperam. Apagar
  `output/*.aux`, `output/capitulos/*.aux` e `output/main.fdb_latexmk` e rodar `pdflatex` uma vez antes do latexmk.
- **Git.** Os remotos do robot-thesis se chamam `overleaf` e `github`.
