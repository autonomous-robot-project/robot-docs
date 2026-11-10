# Notas das verificações fora da monografia

Notas retiradas na conversão das verificações (robot-docs, tag v1.0.1) para LaTeX. Ficam aqui para decidir depois onde entram na monografia.

## V-05

- **Período.** T_c = 10 ms fica abaixo do intervalo entre medidas dos sensores (encoder ≥ s/v_max, VL53L0X ≈ 33 ms). Um período menor não acrescenta informação ao laço.
  - s: deslocamento por pulso do encoder, s = C/N ≈ 10,2 mm (anexo de cálculo do encoder da V-02, Passo 1). v_max = 0,2 m/s (V-06). Nenhum dos dois é definido na V-05.
- **Instrumentação interna em vez do analisador lógico.** O esp_timer tem resolução de 1 µs e custa menos de 1 µs por leitura, bem abaixo de T_c. A instrumentação faz parte do firmware de operação, então C_max e R_max medidos já incluem o seu custo (ADR 028).
- **Tarefas e núcleos.** São três tarefas (ADR 020). A tarefa de controle tem a prioridade máxima, a mesma das tarefas IPC do ESP-IDF, que só rodam quando o outro núcleo as solicita, e fica fixada no núcleo 1. As tarefas de sensor e micro-ROS ficam no núcleo 0, de modo que a tarefa de controle não é preemptada pelas interrupções dos periféricos (UART, GPIO e esp_timer, todas no núcleo 0). No núcleo 1 resta o tick do FreeRTOS, e o seu custo já entra em C_max e R_max.
- **Garantia e medição.** O tempo limitado de cada iteração vem da construção, inspecionada na V-09: sem alocação nem espera bloqueante no laço, e tarefa isolada no núcleo 1. A medição mostra a folga real. O enlace, os sensores e as ISRs rodam no núcleo 0 e não preemptam a tarefa de controle, então a gravação da V-07 já é carga suficiente, sem rodada própria.
- **Reaproveitamento.** A V-08 aplica este critério nas duas condições do deliberador.
  - Ligação já feita pela V-08 (passo 4 e critério RNF-01).

## V-02

- **Anexo de cálculo do encoder** (`verifications/V-02/V-02_calculo_encoder.md`): não entra como anexo do teste. É o projeto da medição de velocidade (deslocamento por pulso, intervalo entre pulsos, t*, v_min, filtro de bordas, limitações); candidato ao capítulo de implementação do controlador.
- Com v_r = 0,2 m/s, o erro limite e_f · v_r é 0,1 m/s.
- (Parte retirada da nota do corte) O corte não estressa motor nem redutor: o motor perde a alimentação e a roda para por inércia, sem corrente de stall. Ao religar, o PI sai da saturação e a roda passa de v_r (até 0,55 m/s, nota 0020), sem efeito no critério.
- O critério de detecção usa T_f = 2 · t_s, com o t_s de projeto. A acomodação medida, de 0,2 a 0,7 s (nota 0011), cabe em T_f, que fica em 1 s.

## V-01

- **Término no sequenciador.** A condição de término fica no sequenciador, que lê a odometria reportada. O controlador converge, restringe e reporta, mas nunca troca de comportamento sozinho (ADR 024). Isso mantém o controlador sem decisão discreta sobre estado interno, como pede o RNF-04. (Decisão de projeto.)
- **Tolerâncias e erros finais.** ε_θ e ε_d precisam ficar acima dos erros finais previstos pela ADR 030 (no exemplo dela, ≈ 3,5° e ≈ 5 mm), somados à resolução da odometria. Na monografia, os dois viraram "de projeto".
- **Alvos de S2 e S3.** θ₁ fica a menos de 180° do rumo atual, como exige a ADR 024. (x₁, y₁) é calculado pelo sequenciador na transição S1 -> S2, a partir de θ₁, e não do rumo alcançado; o resíduo do TURN_TO aparece como erro de ângulo no início do GO_TO. Vai para a descrição da arquitetura (lógica de transição do sequenciador).
- **Resolução da odometria.** ≈ 10 mm por pulso (s) e ≈ 4,2° de giro por pulso de uma roda (s / L_rodas). Vai para a descrição da arquitetura.

## V-03

- **Independência pelas V-09 e V-08.** A V-09 checa no código que o caminho do reflexo não depende de mensagens superiores, e a V-08 verifica que o ciclo de controle, onde o reflexo é aplicado, cumpre os prazos com o deliberador computando e sobrecarregado. Sai: o teste sem os nós do sequenciador e do deliberador já basta; a V-08 cobre a assincronia das três camadas e a V-09 mostra que não há comunicação direta do deliberador com o controlador (Lucas, 9/11).
- **Retomada por rampa.** Decisão de projeto (Alfred, Gat 1998); não muda o critério, só o tempo até a velocidade voltar a v_r. Vai para a arquitetura (conferir a citação de Gat na fonte).
- **Atraso de T_vel.** A velocidade medida só chega a zero depois de T_vel sem bordas, e a retomada até v_r fica mais lenta, porque a medida se atualiza a cada pulso. Sai: não é preciso explicar a retomada no teste (Lucas, 9/11).
- **Tabela falha cognizante (RF-02) × reflexo reativo (RF-03).** O que é detectado, quem age, saída do controlador, persistência e base em Gat. Candidata ao capítulo de arquitetura (conferir as afirmações sobre Gat na fonte).

## V-04

- **Anexo de conversão do plano** (`verifications/V-04/V-04_sequenciador_conversao_plano.md`): não entra como anexo do teste. Descreve como o sequenciador converte o plano (rumo da pose atual ao vértice por atan2, TURN_TO -> GO_TO até o próprio vértice, TWIST(0, 0) após o último; por que partir da pose atual; conformidade com RNF-03, RNF-04 e Gat). Vai para o capítulo de arquitetura, seção do sequenciador (Lucas, 9/11).
- **Sem métrica de seguimento de trajetória.** Cada trecho é um par TURN_TO -> GO_TO em linha reta, sem controlador de seguimento de caminho (ADRs 015 e 042); o RF-07 avalia a sequência dos comportamentos e a pose final. Vai para a arquitetura (Lucas, 9/11).
- **Resolução e sentido travado.** ≈ 10 mm por pulso e ≈ 4,2° de giro por pulso de uma roda; disco de um canal, sentido travado enquanto a roda gira e reavaliado com a roda parada (ADR 019). Vai para a arquitetura, como a nota de resolução da V-01.
- **Regra de vértices (ADR 034).** A nota da sequência recalculada offline ficou na monografia com a ADR 034 em vermelho, até a regra estar descrita na arquitetura; então a nota passa a citar a seção da arquitetura.

## V-06

- **Escolha de T_cmd.** Limite inferior: não parar por perdas ocasionais, T_cmd > (k + 1)/f_cmd; 200 ms = 4/f_cmd tolera k = 2 perdas seguidas. Limite superior: movimento sem supervisão, no máximo v_max · (T_cmd + T_c) ≈ 0,042 m a 0,2 m/s antes de frear, com obstáculos frontais cobertos pelo reflexo (RF-03). Vai para a arquitetura (Lucas, 9/11). Na fonte, "(k + 1)/f_cmd" e "= 4/f_cmd" sem explicar que T_cmd são quatro períodos de republicação, e não um, deixam a nota ambígua.
- **Depois da retomada.** Republicar TWIST move o robô de novo; coerente com o estado efêmero, cada comando novo é um estado novo. Sai (Lucas, 9/11).

## V-07

- **Por que T_seq = 100 ms.** "Gat exige que o sequenciador seja rápido em relação à variação do ambiente no nível de abstração do controlador." A informação nova mais rápida acima do controlador é a varredura do LiDAR, a 10 Hz; T_seq também é menor que T_cmd (200 ms), então o sequenciador reage antes de o vencimento do comando agir. Vai para a arquitetura (Lucas, 10/11). Conferido no excerto de Gat (referencias/excerto_Gat1998.md): "The sequencer should not perform computations that take a long time relative to the rate of environmental change at the level of abstraction presented by the controller". Gat proíbe computações longas no sequenciador, não fixa tempo de reação; "Gat exige que o sequenciador seja rápido" é mais forte que o texto.
- **Reaproveitamento.** A V-08 repete este ensaio nas duas condições do deliberador. Sai: a ligação é feita pela V-08, como na V-05 (Lucas, 10/11).

## V-08

- **Prioridade de tempo real.** O sequenciador e o agente rodam com `chrt -f 50` (frase retirada da nota "C2 verifica a alocação"). Decisão de implantação; vai para a arquitetura (Lucas, 10/11).

# Correções para o robot-docs

Feitas na monografia, a levar para o robot-docs depois que ela estiver pronta.

## V-05

1. Definir q, t_0, k, n, γ e R na tabela de parâmetros.
2. Tirar "Use a instrumentação" do procedimento: a instrumentação está em todos os builds (ADR 028). A descrição da medição vira um parágrafo antes dos passos.
3. Nota Duração: concluir pelo contador da gravação, não por R_max; declarar a independência entre iterações como hipótese do método (Wilks), não verificada; margem reescrita ("para uma iteração não observada perder o prazo, ela precisaria exceder o pior caso registrado em pelo menos T_c − R_max").
4. Nota Valores desde o boot: explicar que o contador no início da gravação pode trazer perdas da partida, por isso a diferença.
5. Critério RNF-01: "nenhuma iteração da gravação perde o prazo (R > T_c)".

## V-02

1. Definir t* (Passo 6 do anexo) e nomear a duração do corte (T_corte = 3 s) na tabela.
2. Passo 4: "repita os passos 2 e 3 até completar três cortes" (o check_v02 espera 3 cortes no total; a rodada final fez 3).
3. Tirar da nota do corte o dado de resultado (até 0,55 m/s, nota 0020).
4. Grafia T_vel em todas as verificações (a V-01 escreve T_VEL).
5. Declarar que T_f = 1 s deixa folga de 0,3 s sobre o t_s medido (0,7 s), e não o fator 2.
6. Critério RF-02 sem janela de tempo, mas o check_v02 julga com janelas (ativo até 2,16 s após o anúncio do corte, inativo até 1,55 s após o religamento). Na monografia: critério pela latência de detecção (t* + T_f) e tolerância de operador e de desaceleração citada em nota, sem números (opção b, Lucas, 9/11). Levar o mesmo texto para a V-02.
7. COAST_DOWN_S = 0,5 s no check_v02 é estimativa ("measure on the bench"), nunca medida; o Passo 8 do anexo diz que é medida na bancada. Medir ou declarar como estimativa.
8. Tabela da V-02 justifica T_vel "reduzido pela reversão (nota 0014)", motivo superado pela ADR 019 (freio da roda em reversão até ser dada como parada). Na monografia: T_vel entre s/v_min ≈ 0,15 s e (1 − e_f)·T_f = 0,5 s, "adotado dentro do intervalo" (Lucas, 9/11).
9. t_s: a tabela define por "2 % do valor final", mas a nota 0011 mediu o assentamento "dentro de 2σ do ruído" (4 a 10 % do valor final em 0,10 a 0,15 m/s). Definições diferentes.
10. t_s não foi medido a 0,2 m/s: os 0,2 a 0,7 s da nota 0011 são dos degraus 0,07→0,10 e 0,10→0,15 m/s; o degrau 0→0,2 tem só o pico. A tabela da V-02 ("medido de 0,2 a 0,7 s") mistura velocidades. Medição possível nas bags da nota 0011 (degrau 0→0,2, tempo até ficar dentro de 2 % do valor final).
11. Na monografia, e_f e v_lim são escritos relativos a v_r, e não à referência depois da rampa (ADR 023), como o firmware faz (Lucas, 9/11). Equivalente nos cortes; nas partidas, o critério com v_r é o caso mais exigente e continua válido (roda abaixo de v_lim por menos que T_f).

## V-01

1. Passo 1 sem "com a frente do VL53L0X livre além de d_stop" (Lucas, 9/11).
2. Regra de sequenciamento: "em repouso" sem "(v = 0 e ω = 0, odometria)"; S4 como TWIST (0, 0), sem "PARAR =" e sem a ADR 030 (Lucas, 9/11).
3. Definir θ e T_vel na tabela de parâmetros. T_vel = 0,3 s é definido na V-01, o primeiro teste que o usa; a V-02 cita a V-01.
4. Grafia T_vel na nota do repouso (a V-01 escreve T_VEL; ver correção 4 da V-02).
5. ε_θ e ε_d marcados "de projeto" na tabela; a nota que os ligava aos erros finais da ADR 030 sai.
6. A nota de resolução cita "ε_g = 0,05 m da V-04", símbolo de outra verificação. Além disso, o que precisa ficar acima da resolução angular (≈ 4,2°) é ε_θ = 10°, não os 90° do giro. A nota saiu da monografia.

## V-03

1. Introdução do teste: a V-03 só tem o título "Teste de reflexo reativo (autonomia do controlador)"; na monografia, o texto do RF-03.
2. Definir T_cmd (200 ms, de projeto; primeiro uso) e T_vel (V-01) na tabela; v_r cita a V-02. A V-06 passa a citar a V-03 para T_cmd.
3. Passo 6: "repita os passos 4 e 5 até completar três bloqueios" (check_v03: EXPECTED_SCREENS = 3; "três vezes" pode ser lido como quatro).
4. Significado de d_stop repete "(ADR 021)", já presente no valor.
5. Critério RF-03 sem janela de tempo, mas o check_v03 julga com janelas: T_settle ≈ 1,25 s do anúncio do anteparo até a velocidade zero (reação do operador 0,5 s e freio 0,05 s estimados, latência do sensor, rampa até v_min, T_vel, atraso do relatório) e T_resume da retirada até v_r (reação, rampa v_r/a_acel, t_s). Mantido o critério; t_o = 2 s cobre T_settle (Lucas, 9/11).
6. Nota nova: por que e_r (amplitude) e não t_s (tempo). Levar o mesmo texto para a V-03.
7. e_r = 0,03 m/s se apoia no ruído de 0,009 a 0,015 m/s (2σ), medido nos degraus de 0,10 a 0,15 m/s, e no sobressinal de até 0,029 m/s do degrau 0 -> 0,2 m/s (nota 0011). O ruído em 0,2 m/s não foi medido (ver correção 10 da V-02).

## V-04

1. Introdução do teste: a V-04 só tem o título "Teste de integração das camadas"; na monografia, o RF-06 e o RF-07 numa frase.
2. Definir n, ε_d (V-01) e d_stop (V-03) na tabela; ε_g = ε_d deixa de trazer o valor "como na V-01" no texto.
3. Nota da sequência recalculada offline cita "a mesma regra", que se referia ao anexo; a regra que o check_v04 aplica é a da ADR 034.
4. Critério RF-07 deixa implícito o que o check_v04 aplica: trechos tirados do Path pela regra da ADR 034 (direções colineares fundidas, tolerância 1e-3 rad; vértice vizinho ao objetivo absorvido, desvio até res/2), alvo do eco comparado ao vértice com tolerância de 1 mm (arredondamento float32), validade com n ≥ 2 e map -> odom identidade. Mantido o critério; só registrado (Lucas, 9/11).
5. Critério RF-07: "o controlador ativa n pares" está errado. É o sequenciador que converte os trechos em pares TURN_TO -> GO_TO e os comanda um a um; o controlador executa cada comando sem registrar o anterior nem prever o seguinte (Lucas, 9/11). Mesma frase no cabeçalho do check_v04 (What e Criterion).

## V-06

1. Introdução do teste: a V-06 só tem o título "Teste de vencimento dos comandos no controlador"; na monografia, a segunda frase do RNF-02 (a primeira fica com a V-09).
2. T_cmd cita a V-03, T_c a V-05 e v_r a V-02; o valor de T_cmd perde o "(= 4/f_cmd)", que só a nota de escolha explicava.
3. Nota Pausas do publicador superada: a pausa de ~330 ms era do transporte padrão do Fast DDS no RPi, eliminada com o Fast DDS só com UDP (nota 0007, ADR 045: 0 pausa em 60 partidas). A rodada final exportou FASTDDS_BUILTIN_TRANSPORTS=UDPv4 (v06_run.sh) e o check_v06 reportou 0 pausas. A nota sai; o PROCEDURE_GAP_MIN_S = 1,0 s do check_v06 e o parágrafo do cabeçalho sobre robot-docs#40 ficam como resto dessa época.
4. A validade do check_v06 (eco mostra o comando publicado antes de cada interrupção) não está na V-06. A rodada final a atendeu em todas as 30 ("command echoed before: True").
5. Nota Repetições: a hipótese (fase uniforme e independente entre interrupções) não é declarada, e a fonte da aleatoriedade é o reinício do publicador a cada repetição, não o instante do Ctrl+C.
6. Nota 0020 dá o atraso de 201,7 a 207,7 ms; o check_v06.txt da mesma rodada dá 200,104 a 209,087 ms. Conferir qual vale.
7. Renomear f_cmd para f_rep (taxa de republicação do comando): com o mesmo subscrito, f_cmd e T_cmd sugerem T_cmd = 1/f_cmd, mas T_cmd = 4/f_cmd (Lucas, 10/11). Ocorrências: V-06, ADR 025, ADR 033, codigo.md e comentários do sequencer_node.py (linhas 9, 87 e 313). O v06_run.sh em evidencias/ fica como está.

## V-07

1. Introdução do teste: a V-07 só tem o título "Teste de velocidade de resposta do sequenciador"; na monografia, a parte medida do RNF-03 (a outra fica com a V-09).
2. Definir Δ, q e γ na tabela; T_seq "de projeto" (a justificativa pelo LiDAR sai); d_stop cita a V-03 e v_r a V-02.
3. Passo 4: Δ parte do t_k do ciclo de controle que ativou o código (ADR 049, check_v07), e não da "borda de subida no Estado (ADR 025)". A borda só aparece no Estado na publicação seguinte, então o texto descreve um instante posterior ao medido; o medido é mais conservador e o resultado não muda.
4. Validade do check_v07 ausente na V-07: índices contíguos, eco em TWIST(v_r, 0) sem código ativo antes de cada ativação, sem lacuna de reinício na Instrumentação. Acrescentada ao critério na monografia; a rodada final a atendeu.
5. "A cada T_ev": pela ADR 049, T_ev é contado a partir do fim do evento anterior; os eventos nunca se sobrepõem.
6. Critério: "Reportar o máximo, a mediana e o percentil 99 de Δ" é instrução de relatório, não critério; sai na monografia.
7. Nota estatística: independência declarada como hipótese do método, não verificada (como na correção 3 da V-05); saem "média e desvio padrão não são usados" e a frase do percentil 99, que repetia o critério.
8. Ordem do método de Wilks: a V-05 diz "pelo mesmo método da V-07", mas na monografia o Teste 5 vem antes; a explicação completa fica no primeiro teste que o usa, e o outro cita.

## V-08

1. Introdução do teste: a V-08 só tem o título "Teste de isolamento temporal da camada deliberadora das demais camadas"; na monografia, o texto do RNF-05.
2. "Demais: herdados da V-07" esconde as variáveis do teste. Na monografia: M (V-04), T_exec = 10 min (novo; o T_e da V-05 vale 5 min), T_c, R, C_max, R_max (V-05), T_seq, Δ, n, T_ev (V-07), v_r (V-02).
3. Passo 3: "Execute a V-07 por 10 min" inclui o passo 1 da V-07 (sem o deliberador), o que contradiz o C1. Na monografia: "com as rodas suspensas, execute os passos 2 e 4 da V-07 e mantenha-os por T_exec".
4. "O plano é entregue ao longo de toda a execução" sem limite: o check_v08_c1 julga com T_gap = 1,5 s (T_plan + 0,5 s, T_plan = 1 s da nota 0019) entre planos consecutivos e entre o início/fim da Instrumentação e o plano mais próximo. Só registrado (Lucas, 10/11).
5. Critério RNF-01: "fim > t_k + T_c em 60 000 iterações" difere do critério da V-05 (correção 5 da V-05); as 60 000 iterações derivam de T_exec. Na monografia: "nenhuma iteração da gravação perde o prazo (R > T_c)".
6. Critério RNF-03: acrescentado "com a validade daquele teste" (o check_v07 roda no mesmo bag).
7. Critério: "Reportar C_max, R_max e o máximo e o percentil 99 de Δ..." é instrução de relatório; sai.
8. Nota C2: "Gat não restringe o deliberador" -> "não restringe os algoritmos do deliberador", como diz o texto ("There are no architectural constraints on algorithms in the deliberator").
9. Nota SLAM em bancada: o mapa resultante "é inconsistente e não é utilizado" (Lucas, 10/11).
10. Nota Execução combinada reescrita (iterações e eventos derivados de T_exec, T_c e T_ev).

## V-09

1. Introdução do teste: a V-09 só tem o título "Inspeção de código"; na monografia, uma frase tirada da nota "Inspeção, não verificação formal".
2. Coluna "Origem" substituída pela citação do teste do primeiro uso: T_vel e v_min passam para a V-01, e_f e T_f ficam na V-02, T_c na V-05; θ (V-01) entra na tabela.
3. T_vel cita a nota 0014, motivo superado pela ADR 019 (ver correção 8 da V-02).
4. Critério RNF-04: "nunca comanda θ a 180° ou mais do rumo atual" usa θ como alvo do TURN_TO, mas θ é o rumo do robô na V-01. Na monografia: "um alvo de TURN_TO a 180° ou mais de θ".
5. Critério RNF-01: "a tarefa de controle é a única de tempo real" contradiz a nota da V-05 (prioridade máxima, a mesma das tarefas IPC do ESP-IDF). Na monografia: "tem a prioridade máxima".
6. e_f relativo à referência efetiva da roda (depois da rampa), como o código que se inspeciona; na V-02 da monografia, relativo a v_r (correção 11 da V-02). Mantida a diferença (opção a, Lucas, 10/11).
7. As duas notas viram um parágrafo só, sem itens; acrescentado "dos repositórios git do trabalho" (Lucas, 10/11).
8. Critério RF-02: "com referência ≥ v_min" exclui a ré; o código e a evidência usam |v_ref| (inspecao.md: `observable = |ref| >= V_MIN`, erro `> E_F·|ref|`). Na monografia, v_ref definido na tabela (primeiro uso; referência da roda depois de reflexos, vencimento e rampa, ADR 023), critério com |v_ref| ≥ v_min e erro acima de e_f · |v_ref| (Lucas, 10/11).
9. Critério RF-06 e RNF-03: "busca nem projeção temporal" -> "busca nem planejamento", como no RNF-03 ("projeção temporal" é de Gat, não do requisito).
10. Critério RNF-01: "a tarefa de controle não faz I/O" -> "não espera por I/O" (ADR 020); a tarefa escreve o duty LEDC e lê dois GPIO de teste (inspecao.md).
11. Critério RNF-02: "todo estado interno" -> "toda representação interna do mundo", como no requisito.
12. Critério RNF-04: os dois subitens (saída do GO_TO tende a (0, 0); alvo do TURN_TO a menos de 180°) ligados à continuidade da saída, como na ADR 024.
