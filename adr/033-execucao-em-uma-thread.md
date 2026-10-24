---
data: 2026-10-24
status: provisório
camada: "sequenciador"
revoga:
revogada_por:
affects: []
evidence: [V-07, V-08]
---
# 033 – Execução em uma thread com publicação imediata

## Problema

Como o nó do sequenciador (ADR 031) agenda os callbacks e quando publica o comando? A reação a uma borda no Estado precisa ficar bem abaixo de T_seq (RNF-03), sem ser atrasada pela consulta ao deliberador (RNF-05), e o comando precisa ser republicado a F_CMD = 20 Hz para não vencer (RNF-02).

## Decisão

- Todos os callbacks rodam num executor de uma thread.
- A consulta ao deliberador é assíncrona: o planejamento roda em outro processo, e a resposta chega como callback.
- Toda transição de passo (ADR 032) publica o comando novo no próprio callback que a decidiu. O timer de 20 Hz só republica o comando vigente.

## Alternativa descartada

- **Executor multithread com grupos de callback:** o GIL serializa os callbacks Python, então não há paralelismo, e o estado do sequenciador passaria a precisar de lock.
- **EventsExecutor (experimental):** menos overhead por callback, mas experimental. Entra só se a medição mostrar o executor como gargalo.
- **Publicação só pelo timer:** a reação herdaria a fase do timer, com até um período de republicação (50 ms) de atraso, metade de T_seq.

## Racional

- RNF-03: com o planejamento fora do processo, nenhum callback do nó é longo. A espera de uma borda se limita aos callbacks já na fila, todos curtos.
- RNF-05: a computação longa fica no deliberador, em processo próprio. O sequenciador só recebe o resultado.
- Uma thread: o estado da ADR 032 (passo atual, máscaras anteriores, pose) não tem acesso concorrente.
- RNF-02: o timer mantém o comando vivo. Envios duplicados perto de uma transição são inofensivos, porque o controlador usa o último valor e a idade (ADR 017).

## Nota

- O predicado de término é avaliado na Odometria (20 Hz), onde a pose muda. O Estado (100 Hz) só gera bordas.
- As pausas do coletor de lixo e a prioridade de tempo real ficam para a decisão de implantação no RPi.
