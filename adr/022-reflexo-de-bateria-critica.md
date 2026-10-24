---
data: 2026-10-23
status: provisório
camada: "controlador"
revoga:
revogada_por:
affects: []
evidence: [V-03, V-09]
---
# 022 – Reflexo de bateria crítica sem retenção

## Problema

Com os motores parados, a tensão da bateria se recupera. Depois de disparar, um reflexo de bateria crítica pode liberar e voltar a disparar em ciclo, descarregando ainda mais uma bateria já no limite.

## Decisão

Abaixo de V_CRIT, medido sobre a tensão filtrada, a referência vai a zero. O reflexo libera sozinho quando a tensão filtrada volta acima de V_CRIT, sem retenção nem histerese. Cada episódio é reportado ao sequenciador.

## Alternativa descartada

- **Retenção até reiniciar:** estado que não vence, contra o RNF-02, e que tira do sequenciador a decisão de recuperação.
- **Histerese no controlador:** decisão discreta sobre estado interno, que pertence ao sequenciador.

## Racional

- Gat admite no controlador estado de filtragem e estado efêmero, não estado de decisão. A média da tensão é filtragem; o resto é comparação sem estado.
- O reflexo é a última barreira, não o mecanismo normal de parada. Com o sequenciador vivo, o limiar de aviso (com histerese) encerra a missão antes de V_CRIT. Com o RPi travado, o vencimento do comando já zera a referência (RNF-02).
- A oscilação só ocorre se o sequenciador ignorar o aviso e os episódios reportados. É um defeito do sequenciador, visível e corrigível lá.

## Nota

A constante de tempo do filtro será fixada por medição: longa o bastante para ignorar os picos do PWM e da aceleração.
