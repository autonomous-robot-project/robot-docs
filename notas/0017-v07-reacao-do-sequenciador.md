# V-07, reação do sequenciador - 2026-10-31 - sem commit de código

## Spike de latência com e sem `chrt -f 50` (F6 D5, ADR 039) - frente C

Montagem:
- RPi 5, kernel 6.8.0-1065-raspi, 4 núcleos, sem ROS. 4 laços `while True: pass` em Python, um por núcleo, no lugar
  do `stress-ng --cpu 4` do C2 (não instalado).
- Script descartável (T3): 2000 × `time.sleep(10 ms)` em Python, atraso = tempo medido − 10 ms. Um caso no
  escalonador comum, outro com `sudo -n chrt -f 50`. `throttled=0x0` ao fim.

Medido:

| Caso | Mediana | p99 | Máximo |
| --- | --- | --- | --- |
| Sem carga | 0,059 ms | 0,062 ms | 0,095 ms |
| 4 núcleos saturados | 0,055 ms | 0,059 ms | 3,15 ms |
| 4 núcleos saturados + `chrt -f 50` | 0,005 ms | 0,0065 ms | 0,009 ms |

Figura: 0017-latencia-chrt.png (os dois casos com carga). Numa primeira rodada, com 12 laços (3 por núcleo), o
máximo foi 7,5 ms sem `chrt` e 0,020 ms com ele.

Ajustes:
- Nenhum. A ADR 039 fica: sem carga, o tempo real não muda nada mensurável; no C2, ele tira o atraso de ms. Uma
  acordada só, não a cadeia agente → sequenciador → agente: o Δ da V-07 e da V-08 é a medida.

Surpresas:
- `ulimit -r` = 0 para o usuário: o `chrt` sem root falha. Mecanismo escolhido: `rtprio 50` no
  `/etc/security/limits.d/`, lido pelo `pam_limits` do `sshd` (presente). Aplicado no F6 I3.
- O RPi tem `sudo` sem senha para tudo (`NOPASSWD: ALL`). Os ensaios não dependem disso para o `chrt`.

Aplicado (F6 I3, 2026-10-31):
- `/etc/security/limits.d/99-robot-rtprio.conf` no RPi: `lucasfv - rtprio 50`, com comentário citando a ADR 039.
- Sessão ssh nova: `ulimit -r` = 50, também sob `env -i`; `chrt -f 50 sleep 5` sem sudo → `ps` mostra `FF 50`;
  `chrt -f 51` falha com "Operation not permitted" (o limite vale). Para desfazer, apagar o arquivo.

## Firmware do modo de ensaio gravado (F6 I4, ADR 049) - frente A

Versões: robot-firmware 59beb32, robot-interfaces 774e892, robot-ros-system b71b606. Só a app gravada, com a chave
dos motores desligada; `robot_interfaces` recompilado no `~/robot_ws` do RPi, `robot_verification` em
`~/spike_build_A`.

Medido:

| Item | Resultado | Referência |
| --- | --- | --- |
| `check_link` | PASS: Estado em 0,5 s; após reiniciar o agente, em 0,6 s | — |
| Enlace, ESP32 → RPi (`measure_link_load`, 60 s, comando TWIST(0, 0) a 20 Hz) | 20425 B/s = 22,2 % | ≤ 50 % (ADR 025); 22,0 % na nota 0014 |
| Enlace, RPi → ESP32 | 909 B/s = 1,0 % | ≤ 50 % |
| Instrumentação, uma amostra com o GPIO 12 solto | `test_event_index` = 0, `test_event_response_us` = 0, `deadline_misses` = 0 | modo inerte no boot (ADR 049) |
| `faults` no Estado, uma amostra | 0: sem `FAULT_TEST` nem `FAULT_DEADLINE_MISSED` | — |

Ajustes: nenhum. Os dois campos novos somam 8 B a 10 Hz, abaixo da resolução da medida (+0,2 pp).

## Checagem de bancada da V-07 e da V-05 - 2026-11-02

Montagem: robot-firmware 03c0f35, robot-interfaces 774e892, robot-ros-system e72729d. Rodas suspensas, chave dos motores ligada, frente do VL53L0X livre, sem deliberador, GPIO 7
aterrado durante a gravação (ADR 049). `run_v07`, `check_v07` e `check_v05` no mesmo bag; dados em
`evidencias/V-07/2026-11-02_1933/`. Checagem sobre o HEAD, não a rodada final.

| Medida | Valor |
| --- | --- |
| Eventos com a ativação | 303 de 303, índices contíguos, TWIST(0,2; 0) antes de cada um |
| Δ: mediana · p99 · máximo | 13,6 · 28,3 · 28,5 ms (T_seq = 100 ms) |
| Gravação · maior lacuna da Instrumentação | 348,5 s · 0,120 s |
| Prazos perdidos · C_max · R_max | 0 · 897 µs · 914 µs (folga de 90,9 % de T_c) |

V-07: PASS. V-05: PASS.

Aborto da primeira tentativa (2/11, 18:02): a `v07` abortou 1,2 ms depois de RUNNING. Pelo código, os eventos
próprios não ativam nesse tempo (T_eco = 0,3 s, T_LINK = 0,2 s), então foi um código do controlador já ativo no
primeiro Estado do passo; a `v07` aborta por qualquer código além do `FAULT_TEST`. Causa provável, não conferida:
`REFLEX_FRONT_OBSTACLE` ou `FAULT_FRONT_SENSOR` com a frente do sensor obstruída. Desde robot-docs#51 o log do
sequenciador registra o código; nesta checagem, com a frente livre, não houve aborto.

Emenda ao passo 1 da V-07, com o ok do Lucas: o `run_v07` roda sem o deliberador; a carga do deliberador é a V-08 C1.
