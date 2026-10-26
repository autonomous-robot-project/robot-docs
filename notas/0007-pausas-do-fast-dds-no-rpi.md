# #40 - Pausas de ~320 ms no RPi - 2026-10-25 - commit 14acafa (firmware)

Montagem: RPi 5 (Jazzy, Fast DDS 2.14.6, governor `ondemand`) e ESP32-S3 pelo enlace UART, sem drivers.
Agente micro-ROS rodando. Sondas em Python e C++ com o QoS do enlace (ADR 025), em `~/fw/p40` e `~/fw/p40_ws` no RPi.

Medido:

| Ensaio | Transporte do Fast DDS | Com pausa | Pausa |
| --- | --- | --- | --- |
| Publicador novo de Command a 20 Hz, com `ros2 bag` gravando, 30 partidas | padrão (SHM + UDP) | 5 de 30 | 314 a 334 ms, sempre dentro do 1º `publish()` |
| O mesmo | só UDP | 0 de 30 | `publish()` máx. 0,2 ms |
| O mesmo, com publicador em C++ (rclcpp) | padrão | 5 de 30 | 326 a 333 ms, dentro do `publish()` |
| Assinante novo de State, 30 partidas | padrão | 2 de 30 | 325 e 329 ms, logo após a 1ª mensagem |
| O mesmo | só UDP | 0 de 30 | intervalo máx. 10,6 ms (= T_c) |
| Publicador de vida longa (70 s), com 10 assinantes entrando e saindo | padrão | 0 | `publish()` máx. 0,5 ms |
| Assinante de State de vida longa (70 s), com 10 assinantes entrando e saindo | padrão | 0 | intervalo máx. 13,8 ms |

- Causa: o transporte por memória compartilhada (SHM) do Fast DDS bloqueia por ~320 ms no início da vida de um
  endpoint novo, em parte das partidas. Com o SHM desligado (`FASTDDS_BUILTIN_TRANSPORTS=UDPv4`), some.
  Com 5 pausas em 30 no padrão, a chance de 0 em 30 por acaso é (5/6)^30 ≈ 0,4 %.
- É o bug [#6535 do Fast DDS](https://github.com/eProsima/Fast-DDS/issues/6535): abrir uma porta SHM saudável
  pode esperar healthy_check_timeout_ms / 3 = 333 ms. A correção (PR #6559) mira a v3.6.3, sem backport para a 2.14
  do Jazzy.
- O GC do Python não é a causa: a coleta mais longa levou 2,9 ms.
- A pausa não volta depois da partida: um nó de vida longa não pausa quando outros entram ou saem.

Surpresas:
- O `ros2 topic pub` das pausas da V-06 era só o caso mais visível: o efeito vale para qualquer endpoint novo,
  inclusive assinantes, e também em C++. Não é do Python.

Pendências:
- Nenhuma: transporte decidido na ADR 045.
