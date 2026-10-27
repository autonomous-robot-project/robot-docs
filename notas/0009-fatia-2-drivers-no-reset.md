# Fatia 2, #21 - Drivers no reset e na gravação - 2026-10-26 - commit 37c43b8 (firmware)

Ferramenta: robot-firmware/tools/driver_inputs/in21.py. Evidência: evidencias/nota-0009/2026-10-26/.

Montagem: DRV8871 com VM da 3S pela chave dos motores (fusível de 2 A), motores TT ligados, rodas suspensas.
ESP32 pela USB nativa do RPi. Analisador lógico (clone Saleae, 2 MHz) no RPi: CH0 a CH3 nos IN (GPIO 4, 5, 2, 42),
CH4 no RST e CH5 no GPIO 11.

Medido:

| Situação | IN dos drivers | Rodas |
|---|---|---|
| Firmware rodando, sem comando | freio (IN1 = IN2 = 1, duty 0 em decaimento lento) | paradas |
| Gravação pelo RPi | freio mantido durante toda a gravação; no reset final, como a linha abaixo | paradas |
| Reset pelo RPi (esptool) | livre por ~10 ms no boot, depois freio | paradas |
| Botão RST | 0 V nos IN com o RST apertado, sem o analisador (multímetro) | paradas |
| Watchdog (GPIO 11 no GND) | — (só observação, sem analisador) | paradas |
| Ligar (USB do ESP32 replugada) | — (só observação, sem analisador) | paradas |

- Nas transições do reset, IN1 e IN2 de um driver não mudam juntos: pulsos de tração de 20 a 37 µs no reset e de
  até 50 µs na subida do firmware depois do RST. Nenhum moveu a roda: a constante mecânica do motor é ~0,1 s.
- O pulso do 1º ciclo do LEDC (até 50 µs, arquitetura.md) não apareceu na subida do firmware depois do reset pelo
  RPi.

Ajustes:

- O critério da #21 ficou "nenhuma roda se mexe nas cinco situações", com o nível dos IN medido só onde o
  analisador não altera o circuito (abaixo).

Surpresas:

- O analisador carrega as linhas com um pull-up de ~66 kΩ: com o ESP32 em reset, os IN ficam em ~2 V contra o
  pull-down de 100 kΩ do DRV8871, acima do limiar de nível alto do driver. As leituras em 0 valem; as leituras em 1
  com o pino em alta impedância (RST apertado, boot, ESP32 desligado) são do analisador. Com a ponta de um só IN
  solta, o VM ligado e o RST apertado, o driver viu IN1 = 0 e IN2 ≈ 2 V e o motor girou: mexer nas pontas dos IN só
  com a chave dos motores desligada, ou nas duas do par juntas.
- Na gravação pela USB nativa, os pinos mantêm o último estado (o reset que leva ao modo de gravação não reinicia
  os periféricos), em vez de ir ao nível baixo da ADR 008. Com duty 0 é freio, e as rodas não giram.

Pendências: nenhuma.
