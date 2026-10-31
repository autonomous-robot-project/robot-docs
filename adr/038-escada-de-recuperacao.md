---
data: 2026-10-24
status: provisório
camada: "sequenciador"
revoga:
revogada_por:
affects: []
evidence: [V-01, V-04, V-09]
---
# 038 – Escada de recuperação

## Problema

Uma reação fixa por código (ADR 032) não expressa tentativas sucessivas: esperar, contornar e depois desistir. Esperar por `cleared(code)` sem limite trava o passo diante de um obstáculo que não sai. Qual mecanismo e qual reação a cada código na missão por plano?

## Decisão

Mecanismo:

- `ladder(r1, r2, …)`: na k-ésima ocorrência do código no mesmo passo, aplica r_k; depois do último degrau, `abort()`. O contador zera quando o passo termina com sucesso, não na reentrada.
- `cleared(code, timeout)`: se o tempo estourar com o código ativo, a reentrada gera nova borda (ADR 037) e sobe-se um degrau.
- `replan()`: pede um plano novo da pose atual para o mesmo objetivo, com TWIST(0, 0) enquanto espera. No máximo N_REPLAN por missão; depois, `abort()`.
- `wait_until_clear(code, timeout)`: passo de espera em TWIST(0, 0) que ignora o próprio código.

Tabela da missão por plano:

| Código | TURN_TO | GO_TO |
| --- | --- | --- |
| Obstáculo frontal | `ignore()` | `ladder(recover([wait_until_clear(…, T_WAIT)]), replan())` |
| Falha do sensor frontal | `ignore()` | `ladder(recover([wait_until_clear(…, T_WAIT)]))` |
| Roda travada | `abort()` | `abort()` |
| Bateria crítica | `abort()` | `abort()` |
| Prazo perdido | `ignore()` | `ignore()` |
| Reinício por watchdog | `abort()` | `abort()` |
| `NO_PROGRESS` | `ladder(retry())` | `ladder(retry())` |
| `LINK_LOST` | `abort()` | `abort()` |
| `HEARTBEAT_LOST` | `abort()` | `abort()` |
| `BATTERY_LOW` | `abort()` | `abort()` |
| `COMMAND_NOT_ECHOED`, plano falhou, TF ausente, outros | `abort()` | `abort()` |

## Alternativa descartada

- **Sem escada (só `abort()` e `ignore()`):** cumpre o RF-04, mas reduz o sequenciador à falha cognizante, sem tratar contingências.
- **Contador global de tentativas por missão:** trata todas as falhas igual.
- **Replanejar direto diante do obstáculo:** replaneja por obstáculos passageiros.
- **Nova tentativa diante da roda travada:** insistir força o motor e o driver.

## Racional

- Gat: o sequenciador responde a contingências usando o histórico de execução, sem busca. A escada é esse histórico (quantas vezes neste passo) decidindo a próxima tentativa.
- O giro é permitido sob o obstáculo e a falha do sensor frontal (ADR 021), então o TURN_TO os ignora.
- Bateria baixa encerra a missão antes de V_CRIT, e o reflexo crítico fica como última barreira (ADR 022).
- Bateria crítica encerra a missão (ADRs 009 e 022); o reflexo sem histerese faria o robô alternar entre andar e parar.
- O reinício por watchdog zera a odometria, e os alvos em odom perdem o sentido. Depois de `LINK_LOST`, o sequenciador não sabe se o ESP32 reiniciou (um pânico ou uma queda de tensão não deixam código), então aborta pelo mesmo motivo.
- Heartbeat perdido aborta com TWIST(0, 0) explícito, a parada mais rápida que o sequenciador consegue dar; deixar o comando vencer acrescentaria T_cmd + T_c de movimento. Pausar e retomar faria o robô voltar a andar sozinho quando o heartbeat voltasse, o que contraria uma parada remota.
- O limite de `replan()` por missão evita o ciclo com um obstáculo visto pelo VL53L0X e não pelo LiDAR, em que o plano novo repete o caminho.

## Nota

- Os passos de espera herdam o restante da tabela da missão.
- T_WAIT e N_REPLAN são parâmetros ROS; pontos de partida 5 s e 3.
- As missões de ensaio têm tabelas próprias: a V-01 aborta em qualquer falha; a V-07 e a V-08 usam `wait_until_clear` com o código de ensaio. A V-08 ignora `LINK_LOST` e `COMMAND_NOT_ECHOED`, porque sob C2 o efeito esperado é o vencimento do comando, que também deixa o eco em TWIST(0, 0).
- O heartbeat é exigido por padrão. A V-01, a V-07 e a V-08 declaram `HEARTBEAT_LOST: ignore()` e rodam sem notebook.
- As missões de ensaio também abortam com bateria baixa.
