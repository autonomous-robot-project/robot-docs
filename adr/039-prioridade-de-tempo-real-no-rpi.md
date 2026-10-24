---
data: 2026-10-24
status: provisório
camada: "sequenciador"
revoga:
revogada_por:
affects: []
evidence: [V-07, V-08]
---
# 039 – Prioridade de tempo real no RPi

## Problema

O sequenciador divide o RPi 5 com o deliberador. Ele precisa manter o RNF-03 com o deliberador computando e com a CPU saturada (RNF-05, V-08). O caminho crítico de uma reação passa por dois processos: UART → agente micro-ROS → sequenciador → agente → UART.

## Decisão

O agente micro-ROS e o sequenciador rodam em SCHED_FIFO com a mesma prioridade (`chrt -f 50`), no kernel padrão, sem afinidade de núcleo. O deliberador (Nav2, SLAM) e o `odom_to_tf_ros2` ficam no escalonador comum.

## Alternativa descartada

- **Agente acima do sequenciador:** os dois se alternam no caminho crítico em vez de disputar a CPU; hierarquizá-los não muda nada mensurável.
- **Só o sequenciador em tempo real:** o agente competiria com a carga, e Δ cresceria sob CPU saturada.
- **Kernel PREEMPT_RT:** reduz uma latência de escalonamento que já fica duas a três ordens de grandeza abaixo de T_seq, ao custo de manter outro kernel.
- **Núcleos isolados com afinidade fixa:** tira um núcleo do deliberador sem requisito que peça isso; com SCHED_FIFO, os dois processos já preemptam a carga em qualquer núcleo.

## Racional

- RNF-05: a separação de prioridade é o que isola o deliberador do sequenciador, já que os dois dividem o processador.
- RNF-03: o sequenciador é rápido, sem garantia rígida (Gat). Prioridade de tempo real no kernel padrão é o mínimo que mantém a reação limitada sob carga, e a V-08 C2 mede isso.
- As threads criadas depois do lançamento (DDS) herdam a política do processo.

## Nota

- Se a V-08 C2 reprovar pelo escalonamento, o PREEMPT_RT é o próximo passo.
- Coletor de lixo do Python: nada por enquanto. Se picos de Δ coincidirem com coletas, `gc.freeze()` depois da inicialização é a primeira medida.
- O limite padrão de tempo real do kernel (95 %) fica, para que um defeito no sequenciador não trave o RPi.
