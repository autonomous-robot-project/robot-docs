---
data: 2026-10-31
status: provisório
camada: "controlador"
revoga:
revogada_por:
affects: [robot-firmware/components/controller, robot-firmware/components/link, robot-interfaces/msg]
evidence: [V-07, V-08]
---
# 049 – Modo de ensaio da reação do sequenciador

## Problema

A V-07 mede o tempo de reação do sequenciador (RNF-03) com 300 eventos artificiais gerados pelo controlador, no mesmo binário que opera (ADR 028). É preciso decidir como o modo é ativado, qual código ele usa e entre quais instantes Δ é medido.

## Decisão

- **Ativação por pino:** um GPIO com pull-up interno; nível baixo ativa o modo. Solto, o modo fica inerte, também no boot. Soltar o pino encerra a geração de eventos; um evento ativo termina normalmente.
- **Código próprio:** `FAULT_TEST` em `faults`. Fica ativo até a chegada de um TWIST(0, 0) recebido depois da ativação.
- **Δ = chegada do TWIST(0, 0) − t_k do ciclo que ativou o código**, no relógio do ESP32. A chegada é o carimbo do canal de comando, não o comando em vigor no ciclo.
- **Intervalo entre eventos:** T_ev sorteado no firmware, contado a partir do fim do evento anterior; os eventos nunca se sobrepõem.
- **Publicação:** índice do evento (acumulado desde o boot) e Δ do último evento na Instrumentação.

## Alternativa descartada

- **Comando especial no `Command.msg` ou parâmetro pelo enlace:** o modo ficaria alcançável pela interface de operação; um defeito no sequenciador injetaria falhas falsas. O parâmetro ainda custa entidades micro-ROS (ADR 043).
- **Reaproveitar um código existente:** o sequenciador reagiria ao ensaio como a uma falha real, e o bag não distinguiria os dois.
- **Fim de Δ no ciclo em que o eco vira TWIST(0, 0):** soma até T_c de espera e mede a aplicação, não a chegada que a V-07 define.

## Racional

- Só um ato físico ativa o modo; o padrão é o do gatilho do watchdog da V-02 (ADR 029).
- Início em t_k, antes da publicação do Estado: Δ só pode sair maior que a reação real, o lado conservador para o RNF-03.
- Se o TWIST(0, 0) nunca chega, o código fica ativo e o índice para: a falta de resposta aparece como índices faltando, não como Δ pequeno.
- Δ do último evento, publicado a 10 Hz com eventos de ~1 s, aparece em ~10 mensagens: uma perda não apaga a medida (ADR 028).

## Nota

- Um TWIST(0, 0) republicado antes do evento daria Δ ≤ 50 ms sem reação; a validade "eco TWIST(v_r, 0) antes de cada evento" do `check_v07` rejeita esse caso.
- `FAULT_TEST` dura Δ, abaixo dos 100 ms da ADR 037, por desenho: é mantido por nível até a resposta, e a resposta prova que o sequenciador o viu.
