# V-05, checagem da cadeia do medidor de prazos - 2026-10-28 - commits 171f029 (firmware gravado) e 230ed56 (robot-ros-system)

Ferramentas: robot-ros-system/robot_verification `bench/v05_bench.sh` (agente, bag, comando a 20 Hz e
`measure_link_load`), `check_v05` (critério, T1) e `plot_recording` (uma figura por campo gravado). Evidências:
evidencias/nota-0013/2026-10-28/ (bag, saídas do `check_v05` e do `measure_link_load`, figuras).

O que é: checagem da cadeia `DeadlineMeter` → Instrumentação → bag → `check_v05`, guardada para conferência. Não é a
evidência da V-05, que vem da gravação da V-07 sobre a tag (V-05, procedimento).

Montagem: rodas suspensas, motores TT com DRV8871, bateria 3S, fusível de 2 A. ESP32 pela USB nativa do RPi, enlace
pela UART (ADR 043). Chave dos motores desligada, exceto de ~39 a ~55 s e de ~294 s ao fim, quando foi ligada para
observar a malha.

Carga: TWIST(0,2; 0) a 20 Hz, Estado a 100 Hz e Instrumentação a 10 Hz. Ainda sem Odometria, VL53L0X e GO_TO.

Medido (PASS):

| Grandeza | Valor | Critério ou limite |
|---|---|---|
| Duração da gravação | 381,6 s (3813 amostras da Instrumentação) | ≥ T_e = 300 s |
| Maior lacuna da Instrumentação | 0,110 s | ≤ 1 s (sem reinício) |
| Prazos perdidos na gravação | 0 | 0 |
| C_max (desde o boot) | 425 µs, U = 4,2 % | |
| R_max (desde o boot) | 441 µs, margem 95,6 % | ≤ T_c/2 = 5 ms (medidor validado) |
| Enlace, ESP32 → RPi | 5598 B/s = 6,1 % | ≤ 50 % (ADR 025) |
| Enlace, RPi → ESP32 | 905 B/s = 1,0 % | ≤ 50 % |

Leituras:

- C_max e R_max sobem em degraus até ~100 s (C de 375 a 425 µs, R de 407 a 441 µs) e ficam estáveis nos ~280 s
  seguintes: os máximos desde o boot não vêm só do boot, e ciclos mais lentos aparecem esporadicamente.
- R_max − C_max ≈ 16 µs, a ordem da latência de liberação. t_0 é lido depois do primeiro despertar, então R sai
  menor que o real pela latência desse despertar, também de µs: erro não conservador, três ordens abaixo de T_c.
- C_max ficou acima da estimativa de dezenas de µs feita antes da medida. Com 95,6 % de margem, o custo estimado do
  GO_TO (≤ 20 µs) não muda o veredito.
- Com o VM ligado, as rodas partem com pico de ~0,5 m/s e assentam em 0,2 m/s: o integrador chega saturado pela falha
  (ADR 023). A falha cognizante fica ativa com o VM cortado e se apaga com ele ligado, como na V-02 (nota 0012).

Decisão: os valores instantâneos de C e R não entram na Instrumentação. Nenhum critério depende deles e a margem não
muda o veredito. Se a monografia pedir a distribuição de C, a forma é um histograma acumulado no firmware (sem perda
por best effort, coerente com a ADR 028), não o valor do último ciclo.
