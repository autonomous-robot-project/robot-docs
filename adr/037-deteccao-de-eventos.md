---
data: 2026-10-24
status: provisório
camada: "sequenciador"
revoga:
revogada_por:
affects: []
evidence: [V-01, V-07, V-09]
---
# 037 – Detecção de eventos

## Problema

As reações (ADR 032) são disparadas por bordas de subida nas máscaras do Estado (ADR 025). Uma condição que já está ativa quando a comparação começa não produz borda: um obstáculo presente na entrada de um passo, ou o código de reinício por watchdog (ADR 029), que chega na primeira máscara depois que o enlace volta. Além disso, se o comando deixa de chegar ao controlador e o Estado continua chegando, nada é detectado.

## Decisão

- **Máscara anterior desconhecida vale 0:** ao subir o nó, quando o enlace volta e na entrada de cada passo. Toda condição ativa nesses instantes gera borda de subida, e a tabela do passo decide.
- **Eco do comando:** se o eco do Estado difere do último comando enviado por mais de T_eco, com T_eco acima de T_cmd, o sequenciador gera o evento `COMMAND_NOT_ECHOED` para a tabela de reações.
- **Idade do Estado:** sem Estado há mais de T_LINK = T_cmd, o sequenciador gera o evento `LINK_LOST`. A idade é verificada no timer de republicação (ADR 033), porque o callback do Estado não dispara sem mensagens.
- **Heartbeat (ADR 016):** sem mensagem do notebook há mais de T_HB, a condição `HEARTBEAT_LOST` fica ativa. É tratada por nível, como um bit de máscara, e verificada no mesmo timer.
- **Bateria baixa (ADR 009):** a condição `BATTERY_LOW` fica ativa quando a tensão do BatteryState cai abaixo de V_WARN e só cai acima de V_WARN + H. A histerese fica no sequenciador (ADR 022).

## Alternativa descartada

- **Verificação separada na entrada do passo:** mesmo efeito com dois caminhos de código, sem cobrir o retorno do enlace.
- **Só bordas novas:** perde o obstáculo já presente e o reinício por watchdog.
- **T_LINK curto:** detectar cedo não traz segurança, porque o controlador já para pelo vencimento (RNF-02), e aumenta os falsos positivos sob carga (V-08 C2).
- **Sem conferir o eco:** o enlace quebrado no sentido RPi → ESP32 passaria despercebido, porque o Estado continua chegando.

## Racional

- Gat: o controlador falha de forma cognizante e reporta a condição atual. O sequenciador precisa ver toda condição ativa pelo menos uma vez, qualquer que seja o momento em que começou.
- Uma só regra cobre o início, o retorno do enlace e a entrada de passo.
- RF-01 e RF-04: o eco igual ao enviado é o critério da V-01, aqui como monitor permanente. Isso também cobre o robô que nunca se mexe, sem tempo máximo por passo (ADR 036).
- Os dois sentidos do enlace ficam cobertos: a idade do Estado vê a queda ESP32 → RPi, e o eco vê a queda RPi → ESP32.

## Nota

- Como `HEARTBEAT_LOST` e `BATTERY_LOW` são por nível, uma missão não começa sem heartbeat nem com bateria baixa: a condição ativa na entrada do primeiro passo vira borda.
- Só bordas de subida são detectadas. "Até a condição acabar" é o término por nível `cleared(code)`.
- Com essa regra, um passo pode receber condições que não o afetam, como o obstáculo frontal durante um TURN_TO (ADR 021). A reação `ignore()` declara isso na tabela do passo.
- O código efêmero precisa durar o suficiente para chegar em pelo menos um Estado. Com 100 Hz em best effort, ≥ 100 ms (10 mensagens) é a exigência para a medição da duração dos códigos.
