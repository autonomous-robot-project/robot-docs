# Fatia 1, passo 1: enlace na UART1 e agente micro-ROS - 2026-10-24 - commit 14d0db4 (robot-firmware)

Montagem:
- RPi 5 GPIO 14 (TX) → ESP32-S3 GPIO 18 (RX); GPIO 15 (RX) ← GPIO 17 (TX); GND comum (ADR 043).
- USB do RPi na porta nativa do ESP32-S3: alimentação, gravação (`esptool --no-stub`) e console de log.
- Firmware: componente `link` do zero (transporte UART1 a 921600, sessão com ping a cada 1 s).

Medido (passo 1, com o agente recompilado):

| Caso | Resultado |
|---|---|
| Agente sobe | `/controller` no grafo |
| Agente cai | ESP32 registra a perda em ~1 s (período do ping) e volta a esperar |
| Agente volta | sessão refeita sem reiniciar o ESP32 |
| ESP32 reinicia, agente mantido | sessão refeita 233 ms após o boot, na mesma `/dev/ttyAMA0` |

Surpresas:
- O agente (`~/microros_ws`, compilado em 2025-06) abortava com "stack smashing detected" ao receber
  a primeira mensagem do ESP32. Com o ESP32 em silêncio, a 115200 ou 460800 (bytes ilegíveis) ou por UDP, não.
- Causa: ABI. O agente foi compilado contra o Fast-CDR e o Fast-DDS da época; o apt os atualizou depois
  (Fast-CDR 2.2.7 em 2026-02, Fast-DDS 2.14.6 em 2026-03). Recompilado contra as bibliotecas atuais, funcionou.
- O `esptool` do Ubuntu vem sem o stub flasher: gravar com `--no-stub`.
- `ros2 run` não repassa SIGTERM ao processo filho.

Ajustes (prevenção):
- Pacotes do ROS em hold durante a fase de ensaios (225 pacotes).
- Agente no mesmo workspace do robô (`~/robot_ws`), recompilado junto após qualquer atualização do ROS.
- `check_link` (robot_verification) no início de cada sessão de bancada: PASS em 0,5 s; FAIL com o ESP32 em silêncio.
- Procedimento no README do robot-ros-system, seção "RPi environment".

Pendências:
- `~/microros_ws` antigo (e `build/micro_ros_agent.bak-2025`) ainda no RPi: apagar depois de confirmar o `~/robot_ws`.
