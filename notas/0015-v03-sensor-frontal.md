# VL53L0X: driver, configuração e medição de T_S para a V-03 - 2026-10-30 - robot-firmware 71dbc03 a af79830

Decisões da fatia 4 (#31) tomadas antes do bring-up. Os dados do ensaio sem potência (I3) entram nesta nota.

- **Driver:** porte enxuto da sequência de inicialização e leitura da Pololu (licença MIT) sobre o `i2c_master` do
  ESP-IDF 5.2.6, em `sensing/`, T2. Alternativas: API da ST (maior, para o mesmo uso) e componente do registry.
- **Instrumento de T_S e da tabela de status:** app `tools/front_range` (como o `motor_characterization`), que usa a
  mesma classe do driver e imprime uma linha CSV por medida (instante, distância, status) na console USB, mais um
  script de gravação e resumo no RPi. Descartados: campo no Instrumentation (recompila o micro-ROS e dá só o máximo,
  sem a tabela de status) e log no firmware de produto (código de ensaio fora de `tools/`). Limitação: o app mede
  sem a micro-ROS no núcleo 0; o intervalo é ditado pelo sensor e a tarefa de sensor tem prioridade acima da
  micro-ROS (ADR 020), então a diferença esperada é da ordem de uma transação I²C (a confirmar).
- **Configuração:** timing budget de 33 ms em modo contínuo (padrão da Pololu). O modo de 20 ms reduziria v·T_S em
  ≈ 2,6 mm por intervalo a 0,2 m/s, com mais ruído perto de d_stop; o contínuo temporizado só somaria latência.
- **Falha de I²C:** timeout T_I2C por transação; depois de N_I2C falhas seguidas, espera bloqueante T_retry,
  reset do barramento (`i2c_master_bus_reset`, pronto no IDF 5.2.6, solta um SDA preso) e reinicialização do
  sensor. Cobre o sensor que reinicia em standby por mau contato, que só o timeout nunca recuperaria. Nenhuma V-NN
  exercita a recuperação; a segurança vem do envelhecimento da medida (ADRs 020 e 021). T_I2C = 10 ms (mais de 30×
  a transação mais longa), N_I2C = 3 (tolera uma falha isolada), T_retry = 500 ms (sensor ausente logado a 2 Hz),
  constantes no `config.h`.
- **Reporte da falha do sensor:** obstáculo em `reflexes` (`REFLEX_FRONT_OBSTACLE`), falha em `faults`
  (`FAULT_FRONT_SENSOR`). Com o anteparo, a falha produz o mesmo efeito do obstáculo; em `faults`, o critério da
  V-03 ("sem código de falha ativo") já a exclui, sem emenda. Alternativa descartada: 2 bits em `reflexes`, que
  pediria emendar a V-03. A linha saiu da tabela de reflexos do `arquitetura.md` e foi para "Falhas reportadas".
- **Janelas do anteparo no `check_v03`:** marcadores "anteparo colocado" e "anteparo retirado" publicados pelo
  `run_v03` no fim de uma contagem regressiva, como na V-02. Velocidade zero julgada em [colocado + T_settle,
  retirado]; volta a v_r depois de retirado + T_resume. T_settle e T_resume são constantes decompostas no I6
  (reação humana, rampa com a_dec, T_vel). Erro do operador só reprova, nunca aprova. Alternativa descartada:
  janelas pelas bordas do `REFLEX_FRONT_OBSTACLE`, que julgariam o controlador pela própria detecção.

## Ensaio sem potência (I3), 2026-10-30

Ferramentas: robot-firmware/tools/front_range (app e `front_range.py`), como rodaram. Evidências:
evidencias/nota-0015/2026-10-30/ (CSVs e `*_resumo.txt`; os de 4 colunas, sem sinal, resumidos pelo `front_range.py`
do commit 5357d20, os demais pela versão com sinal). Montagem: módulo genérico tipo GY-530 solto na bancada, chave
dos motores desligada, quarto com iluminação LED, à noite. XSHUT a 2,79 V com VIN a 3,29 V (pull-up do módulo; fica
solto). O módulo tem uma capa preta fixa sobre o sensor, com janela que só passa IR; não sai.

Bring-up: inicialização e leitura de primeira, sem nenhum erro de I²C nas gravações sem desconexão (pull-ups do
módulo e leitura com repeated start confirmados). Intervalo entre medidas de 29 a 32 ms com medida completa (budget de
33 ms valendo); a medida que falha termina em ~15 ms. Status do sensor conferidos no `vl53l0x_device.h` do ST
(cópia da Adafruit): 6 = RANGEPHASECHECK, 9 = PHASECONSISTENCY, 11 = RANGECOMPLETE.

Offset: o registrador de offset (0x28) veio de fábrica com +53,5 mm (0x00D6), e mesmo assim o sensor lia longe
(contra a segurança). Pontos medidos com régua, mediana da leitura: 50 mm → 88 mm (anteparo branco), 78,4 mm →
121 mm (outro anteparo), 240 mm (±10 mm) → 284 mm (branco). A reta pelos pontos brancos (leitura = 1,032·real +
36,4 mm) dá desvio de 41,1 mm em d_stop; o ganho não é distinguível de 1 com a incerteza do ponto de 240 mm. Decidido
(A1): offset absoluto RANGE_OFFSET_VLX_UM = 53,5 − 41,1 = 12,4 mm escrito no registrador a cada inicialização
(absoluto porque o sensor não reinicia junto com o ESP32). Conferência: 240 mm → 238 mm; 100 mm → 100 mm (95 a
105 mm). A biblioteca da Adafruit (API completa do ST) não corrigiria: a correção de offset da NVM só entra com
`USE_IQC_STATION`. Alternativa de hardware conhecida: VL6180X (até 50 cm, mais preciso), não adotado.

| Cenário | Medidas | Status | Distância (mediana, faixa) | Sinal por SPAD (MCPS) |
| --- | --- | --- | --- | --- |
| Anteparo branco a 100 mm | 1952 | 100 % 11 | 97 (92 a 102) mm | 1,13 a 1,17 |
| Anteparo a ~1 cm | 1955 | 100 % 11 | 15 (10 a 20) mm | 16,5 a 18,3 |
| Frente livre (≥ 2 m, nada no cone) | 1941 | 99,9 % 11, 0,1 % 9 | 0 mm em todas as de status 11 | 0,0015 a 0,0024 |

Falso alvo: com a frente livre, o sensor reporta status 11 com 0 a 87 mm em 74 a 99,9 % das medidas (gravações
i3_c_*), mesmo apontado para espaço aberto. O sinal por SPAD separa o falso alvo do alvo real por ~470× (alvo branco
a 100 mm) e ~7000× (alvo a ~1 cm): é crosstalk da capa. A API do ST descarta esse retorno em software (checagem de
sigma, ligada por padrão com 18 mm, e o "range ignore threshold" por sinal por SPAD, manual UM2039); a Pololu, e o
porte, não. O limiar e a tabela de status são a D6.

Recuperação (D4), VCC do sensor desconectado à mão: 4 leituras falhas, 25 tentativas de inicialização a cada ~0,5 s
(as primeiras chegam à calibração e falham, depois falham no model id) e retomada sozinha, sem reiniciar o ESP32;
lacuna de 14,8 s com o fio fora por ~2 s: depois de religado, o sensor ficou ~10 s sem responder ao model id
(causa não investigada; a segurança vem do T_S). Bug achado no `front_range.py` (T1): as linhas de log coloridas não eram contadas; corrigido.

A refazer com o suporte montado no protótipo: o offset (o valor é deste módulo e desta montagem) e o sinal do falso
alvo (o crosstalk depende do que fica diante da capa).
