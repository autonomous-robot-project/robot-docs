---
data: 2026-10-24
status: provisório
camada: "controlador / sequenciador"
revoga:
revogada_por:
affects: []
evidence: [V-05, V-06, V-07]
---
# 043 – Meio físico do enlace

## Problema

A ADR 012 fixa o protocolo (micro-ROS sobre serial), mas não o meio entre o RPi e o ESP32-S3. O devkit oferece três caminhos: os pinos de UART, a USB do conversor CP2102 e a USB nativa. Qual deles dá menor latência, menos overhead e reconexão mais confiável?

## Decisão

- UART direta: GPIO 14/15 do RPi (`/dev/ttyAMA0`) ligados à UART1 do ESP32-S3, a 921600 baud, com três fios (TX, RX e GND) em 3,3 V nos dois lados.
- A USB nativa do ESP32-S3 fica para alimentação na bancada, gravação e console de log, fora do enlace.

## Alternativa descartada

- **USB pelo CP2102:** a porta persiste no reinício do ESP32, mas o caminho ganha o buffer do conversor e o quadro USB de 1 ms, com jitter que entra nas medições da V-05 e da V-07.
- **USB nativa (Serial/JTAG):** a porta some e reaparece a cada reinício do ESP32, e o agente precisa reabri-la.

## Racional

- RNF-01 e RNF-03: a latência do enlace é só a serialização (≈ 11 µs por byte), sem um conversor ou um quadro USB entre as camadas.
- RNF-02 e ADR 038: a porta do RPi nunca desaparece. Um reinício por watchdog (ADR 029), que a V-02 provoca de propósito, só derruba a sessão micro-ROS, e o ESP32 se reconecta ao mesmo agente.
- O overhead é o mínimo da UART (start e stop), com o enlace em ≈ 20 % de ocupação (ADR 025).

## Nota

- Pinos provisórios no ESP32-S3: GPIO 17 (TX) e 18 (RX), fora dos pinos de strapping. Revistos no mapeamento geral de pinos.
- No RPi, a UART0 nos GPIO 14/15 vem do overlay `uart0-pi5`, sem console do Linux nela.
