# V-02, v_min e T_vel em malha fechada no motor - 2026-10-27 - commits ad3cd2b (firmware gravado) e a394b10 (robot-ros-system)

Ferramentas: robot-ros-system/robot_verification `run_closed_loop` (conduz e grava o bag), `measure_closed_loop`
(critério, T1) e `plot_closed_loop` (figuras). Evidências: evidencias/nota-0011/2026-10-27/ (bag, saída do
measure e figuras).

Montagem: a da nota 0010 sem o AO dos encoders: rodas suspensas, motores TT com DRV8871, bateria 3S a 12,23 V nos
terminais da chave, fusível de 2 A. ESP32 pela USB nativa do RPi, enlace pela UART (ADR 043).

Sequência: 0 por 2 s, 0,2 m/s por 3 s, 0 por 3 s, 0,07, 0,10 e 0,15 m/s por 8 s cada, 0 por 3 s, a 20 Hz.

Medido (PASS):

| Verificação | Roda esquerda | Roda direita | Critério |
|---|---|---|---|
| Parada de 0,2 m/s: velocidade zero após | 0,77 s | 0,77 s | ≤ 1,02 s (esperado 0,82 s) |
| 0,07 m/s, últimos 5 s: média / dispersão | 0,070 / 6 % | 0,070 / 2 % | nunca zero, dispersão < 20 % |
| 0,10 m/s | 0,100 / 5 % | 0,100 / 3 % | idem |
| 0,15 m/s | 0,151 / 5 % | 0,150 / 3 % | idem |
| FAULT_COGNIZANT na rodada | 0 | | nenhum |

- O esperado da parada vem da rampa: a referência cai a A_DEC = 0,5 m/s² e cruza v_min em 0,26 s, o PI freia, e a
  velocidade zera T_vel = 0,51 s depois da última borda. A parada segue a rampa (0,4 s de 0,2 a 0), não o freio
  total de ~50 ms da nota 0010.

Ajustes:

- v_min = 0,07 m/s confirmado no motor: em regime, sem ciclo-limite nas duas rodas. Deixa de ser provisório.
- T_vel = 0,51 s confirmado: a velocidade zera depois da parada e não volta.
- Comparação de float32: os campos `linear` chegam do bag como float32 (0,2 vira 0,20000000298), e o
  `math.isclose` com a tolerância padrão (1e-9 relativa) os rejeitava. A primeira análise saiu INVALID por isso.
  Corrigido com `is_close_float32` (tolerância relativa 1e-6) no `recording.py`, usado pelo `measure_closed_loop` e
  pelo `check_v02`, que tinha o mesmo defeito e daria a V-02 como inválida. O `synthetic.py` passou a arredondar os
  comandos para float32, e os testes antigos falharam até a correção.

Surpresas:

- Sobressinal, por transição (pico; regime nos últimos 5 s do degrau):

  | Transição | Pico (esq. / dir.) | Sobressinal | Ruído (2σ) | Dentro de 2σ após |
  |---|---|---|---|---|
  | 0 → 0,07 | 0,147 / 0,154 | +0,08 m/s (~110 %) | 0,003 a 0,008 | ~2,8 s |
  | 0,07 → 0,10 | 0,116 / 0,112 | +0,012 a 0,016 | 0,006 a 0,010 | 0,5 a 0,7 s |
  | 0,10 → 0,15 | 0,162 / 0,161 | +0,011 | 0,009 a 0,015 | 0,2 a 0,5 s |
  | 0 → 0,2 | 0,229 / 0,215 | +0,015 a 0,029 | — | — |

  - Do repouso em baixa velocidade, atrito estático: a roda só parte com duty ~0,1 (nota 0010), que em giro livre dá
    K · 0,1 ≈ 0,13 m/s. O integrador sobe até lá (Ki · 0,07 = 0,49 duty/s, ~0,17 s), a roda se solta e passa de
    0,07 m/s. Nenhuma sintonia do PI tira isso; só uma compensação de atrito, que depende do atrito no chão (#27).
  - Com a roda girando, atraso da rampa: o sobressinal é ~0,012 a 0,016 m/s absolutos nos degraus de 0,03 e de
    0,05 m/s. Se viesse da sintonia, cresceria com o degrau; constante, é o atraso acumulado da malha com integrador
    seguindo a rampa de A_ACCEL. Fica em ~2σ do ruído e assenta em 0,2 a 0,7 s (projeto: 0,5 s), dentro do T_f.
  - Decisão: a sintonia fica. Nenhum requisito limita o transitório, e na V-02 (0,2 m/s) a acomodação cabe no T_f.
  - Risco: partindo do repouso em baixa velocidade, a roda oscila por ~3 s, e a falha cognizante dispara com erro
    acima de 50 % por T_f = 1 s seguido. Aqui não disparou; no chão, com mais carga, pode disparar.
- Na partida a 0,2 m/s, a primeira leitura vem ~0,5 s depois do comando: a rampa (A_ACCEL = 0,25 m/s²) cruza v_min
  em 0,28 s, e a primeira velocidade precisa de duas bordas.

Pendências:

- Emenda da V-02: v_min "≈ 0,07 m/s, provisório" passa a medido (esta nota).
- Comentário do V_MIN_CONTROL no control_config.h ("provisional, to confirm with the motor") passa a citar esta
  nota.
- #44: sobressinal na partida em baixa velocidade e risco de falso FAULT_COGNIZANT no chão, junto da #27.
