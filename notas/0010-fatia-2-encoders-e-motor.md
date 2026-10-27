# Fatia 2, passos 3 e 4 - Encoders e caracterização do motor - 2026-10-27 - commits cda7ba7, d918f60, c08916f (firmware)

Ferramentas: robot-firmware/tools/encoder_ao (AO dos encoders contra as fendas contadas, por degrau) e
robot-firmware/tools/motor_characterization (rampas lentas nas duas direções).
Evidências: evidencias/nota-0010/2026-10-27_encoder_ao/ (CSV, figuras e contagens) e
evidencias/nota-0010/2026-10-26_rampas/ (CSV e zona morta).

Montagem: rodas suspensas, motores TT com DRV8871 em decaimento lento, bateria 3S a 12,24 V nos terminais da chave,
fusível de 2 A. AO do encoder esquerdo no GPIO 6 e do direito no GPIO 7, só para o diagnóstico.

Medido (encoder corrigido; contagem do firmware = fendas no AO em todos os 27 degraus que giraram):

| | K (m/s por duty, até 0,48) | v no duty 0,48 | τ (degraus ≥ 0,3) |
|---|---|---|---|
| Esquerda, frente | 1,34 | 0,63 m/s | 41 a 57 ms |
| Esquerda, ré | 1,45 | 0,65 m/s | 42 a 56 ms |
| Direita, frente | 1,25 | 0,58 m/s | 30 a 35 ms |
| Direita, ré | 1,00 | 0,49 m/s | 31 a 41 ms |

- Zona morta (rampas de 20 s): a roda parte com duty 0,093 a 0,118 e para abaixo de 0,043 a 0,045, nas duas
  direções. O 0,019 da direita para frente em zona_morta.txt vem de duas bordas falsas antes da partida.
- Tensão média no motor (multímetro) = 11,9 V · duty, igual nas duas rodas e direções, de 1,13 V a 6,51 V: queda
  de ~0,35 V da bateria até o motor. Velocidade linear na tensão até 6,5 V, sem saturação.
- Freio total: a roda para em ~50 ms a partir de 0,6 a 0,8 m/s.
- K da mesma roda variou entre rodadas (esquerda no 0,48: 0,50 e 0,63 m/s), com a roda e o disco oscilando um
  pouco: atrito que muda. Para o PI, é variação de ganho da planta, que o integrador absorve.

Ajustes:

- Encoder: a fenda conta quando o nível amostrado a cada 500 µs fica alto por 2 ms depois de estável em baixo; o
  instante é o da última borda de subida vista pela ISR. A janela de 2 ms é maior que a oscilação do comparador e
  menor que meia fenda em v_max (10 ms a 0,5 m/s). Substitui o filtro de 15 ms entre bordas.
- PI: K = 1,3 m/s e τ = 0,04 s (medianas), no lugar de 1,4 e 0,1 provisórios. O projeto discreto não muda: com o
  ZOH do PWM e o atraso de um ciclo da medição, o motor é G(z) = b / (z (z − a)), a = e^(−T/τ) = 0,779 e
  b = K (1 − a) = 0,288. O zero do PI cancela a, a malha fica z² − z + Kp b = 0, e o polo dominante
  p = e^(−T/(t_s/4)) = 0,923 (t_s = 0,5 s) dá Kp = p (1 − p) / b = 0,247 e Ki = Kp (1 − a) / (a T) = 7,01 (antes
  0,533 e 5,60). Testes do host: acomodação em 410 ms e v_min = 0,07 m/s mantido dentro de 2 %.

Surpresas:

- O comparador do módulo do encoder não tem histerese: a saída digital oscila nas duas transições de cada fenda
  (mais de uma borda por transição em velocidade baixa; ~4,8 contagens por fenda no duty 0,1). O AO é limpo, de
  ~0,1 a ~3,1 V, e nenhuma fenda falha: disco e alinhamento estão bons.
- O filtro de 15 ms mascarava isso entre ~0,15 e ~0,5 m/s, onde a borda falsa cai a meio período da verdadeira.
  Abaixo de ~0,15 m/s ela passava e a velocidade saía dobrada, justamente perto de v_min.
- As caracterizações de 26/10 sem o filtro deram velocidades ~2× as reais (K ≈ 2,9) e "bordas perdidas" que eram
  a falta da borda falsa. Foram descartadas; só a zona morta das rampas vale, porque vem da primeira e da última
  borda.

Pendências:

- K e τ com o robô no chão (#27).
- Opção a decidir: comandar o motor em volts e converter com a tensão da bateria (duty = V / V_bat, divisor do
  GPIO 1), para o ganho da malha não cair com a descarga.
- Testes de bancada do passo 4: zero após T_vel e o limite de baixa velocidade em malha fechada.
