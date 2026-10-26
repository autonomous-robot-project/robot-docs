# Fatia 2, passo 4 - Encoders - 2026-10-25 - commit b227dd0 (firmware)

Montagem: pendente (motor TT com encoder óptico de canal único, 20 fendas, roda suspensa).

Medido: pendente.

Ajustes:

- Bordas por ISR de GPIO, sem o PCNT. O PCNT conta bordas, mas não marca o instante de cada uma, e a velocidade
  vem do intervalo entre bordas (V-02, passo 4): a contagem por período dá resolução de ~1 m/s com 20 fendas
  (V-02, passo 3). Usar o PCNT para ter o instante exigiria uma interrupção por contagem, a mesma ISR com um
  intermediário. O filtro de glitch dele (até ~12,8 µs) não substitui o filtro de repique de 15 ms (V-02, passo 9).
- Nenhuma biblioteca trata encoder de canal único: as prontas (PCNT) são para quadratura. O código próprio
  (WheelEncoder e WheelSpeed) é consequência do hardware fixado (ADR 019). Com encoder de quadratura de alta
  resolução (ex.: JGB37-520 com Hall, ~1320 contagens por volta), a contagem por período no PCNT bastaria e o
  sentido viria do hardware; trocar exige revogar a ADR 019 e refazer s, v_min e T_vel da V-02.
- A velocidade por roda vai no Instrumentation (10 Hz), não no State: o consumidor é a verificação, e o
  sequenciador raciocina sobre a falha já detectada pelo controlador (ADR 025, Gat). A taxa para medir o tempo
  de acomodação fica para o passo 6.

Surpresas:

Pendências:

- Conferir na bancada: velocidade com a roda girando, zero após T_vel, filtro de repique.
