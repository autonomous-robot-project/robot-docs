---
data: 2026-10-25
status: provisório
camada: "sequenciador / deliberador"
revoga:
revogada_por:
affects: []
evidence: [notas/0007-pausas-do-fast-dds-no-rpi.md]
---
# 045 – Fast DDS só com UDP no RPi

## Problema

Com o transporte padrão do Fast DDS (memória compartilhada mais UDP), um processo ROS recém-iniciado às vezes fica ~330 ms sem publicar ou sem receber. É um bug do Fast DDS ([#6535](https://github.com/eProsima/Fast-DDS/issues/6535)): abrir uma porta de memória compartilhada pode esperar um terço do timeout de verificação da porta. O efeito aparece em Python e em C++ (nota 0007). A correção mira a série 3 do Fast DDS, e o Jazzy usa a 2.14.

## Decisão

Todos os processos ROS do RPi usam só o transporte UDPv4 (`FASTDDS_BUILTIN_TRANSPORTS=UDPv4`).

## Alternativa descartada

- **Transporte padrão, com os ensaios ignorando o início dos processos:** cada ensaio teria de contornar a pausa, e a trava ocorre segurando o mutex de envio do participante, então um nó já rodando também poderia travar ao abrir a porta de um leitor novo.
- **Timeout de verificação menor, num perfil XML:** só encurta a espera e acrescenta um arquivo de configuração.
- **Fast DDS 3 ou outra distribuição do ROS 2:** a correção ainda não foi publicada, e trocar a base invalida o que já está validado no Jazzy.

## Racional

- RNF-03: o sequenciador reage em menos de T_seq = 100 ms, e uma pausa de 330 ms passa disso três vezes.
- Com UDP, 0 pausa em 60 partidas, contra 7 em 60 no padrão. O estado chega com o mesmo intervalo máximo (10,6 ms), então o custo do UDP local não aparece nas taxas do projeto.
- Uma variável de ambiente, sem código e sem arquivo novo.

## Nota

Revisar quando a correção do #6535 chegar à distribuição do ROS 2 do RPi.
