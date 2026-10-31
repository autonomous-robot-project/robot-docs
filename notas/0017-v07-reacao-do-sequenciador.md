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
