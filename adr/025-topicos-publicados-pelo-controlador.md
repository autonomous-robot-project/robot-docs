---
data: 2026-10-23
status: provisório
camada: "controlador"
revoga:
revogada_por:
affects: []
evidence: [V-05, V-07]
---
# 025 – Tópicos publicados pelo controlador, taxas e QoS

## Problema

O controlador publica dados com consumidores e taxas diferentes por um enlace UART de ≈ 92 kB/s. Novos dados ainda devem surgir, e é preciso um critério para encaixá-los.

## Decisão

| Tópico | Tipo | Conteúdo | Taxa | Consumidor |
| --- | --- | --- | --- | --- |
| Estado | Próprio | Falhas ativas e reflexos ativos (máscaras de 64 bits com códigos do `robot-interfaces`), eco do comando (comportamento ativo e parâmetros em vigor) | 100 Hz (= 1/T_c) | Sequenciador |
| Odometria | Odometry | Pose e velocidade | 20 Hz | Sequenciador, TF/SLAM |
| Bateria | BatteryState | Tensão filtrada | ~1 Hz | Sequenciador |
| Instrumentação | Próprio | C_max, R_max, prazos perdidos; Δ e índice do evento (V-07) | 10 Hz | Verificação |

QoS de todos os tópicos do enlace, inclusive o comando (ADR 024): best effort, volatile, keep last com profundidade 1. Os consumidores devem pedir a mesma QoS.

Critério para dados novos:

1. Por padrão, o dado entra no Estado.
2. Um tópico novo só se justifica por consumidor diferente, por taxa pelo menos 10 vezes diferente ou por estouro de banda.
3. A taxa é a menor que atende ao consumidor.
4. Eventos são publicados como condição ativa, nunca como mensagem única.
5. A ocupação total do enlace fica em até 50 %.

## Alternativa descartada

- **Tópico único agregado:** mistura a interface da arquitetura com a instrumentação de ensaio, e a Odometry a 100 Hz ocuparia ≈ 76 % do enlace.
- **Um tópico por dado:** multiplica mensagens e caixas de correio, sem consumidor que precise disso.
- **Contador de episódios no controlador:** é estado que não vence (RNF-02), e contadores pertencem ao sequenciador.
- **Lista de códigos ativos:** tamanho variável, que exige pré-alocação e complica o retrato atômico.
- **QoS reliable:** retransmissões atrasam o dado novo atrás do velho e podem bloquear a tarefa micro-ROS à espera de confirmação. Não há ganho quando a próxima mensagem já traz o estado completo.

## Racional

- Todo dado é de último valor e toda condição é publicada como estado atual (ADR 017). Perder uma mensagem não perde informação, e best effort com profundidade 1 entrega sempre o mais recente.
- O sequenciador detecta o início e o fim de cada condição comparando retratos sucessivos. Contagem de episódios e tentativas fica com ele, e o controlador não guarda histórico (RNF-02).
- Códigos definidos como constantes no `robot-interfaces` são compartilhados pelas duas pontas. As máscaras de tamanho fixo cabem num único retrato atômico, sem alocação.
- O comando já tolera perdas pelo vencimento: T_cmd cobre quatro republicações a f_cmd (RNF-02).
- O Estado a 1/T_c é a maior taxa útil. Mantém a V-05 como ensaio de pior caso e dá a maior folga ao RNF-03.
- A Odometria a 20 Hz fica no dobro da taxa do LiDAR, o suficiente para o TF interpolar a pose de cada varredura. Ocupação total ≈ 20 %.
- O eco do comando permite conferir, no lado do RPi, que o controlador aplica o comportamento e os parâmetros enviados (RF-01). É o comando em vigor no ciclo: o recebido ou, depois do vencimento, TWIST(0, 0) (RNF-02). Os reflexos não alteram o eco e aparecem nas máscaras. Acrescenta dois valores de ponto flutuante e não altera a ocupação de forma significativa.
- Tipos padrão saem prontos do ESP32 sempre que cabem no orçamento, sem tradutor no RPi (ADR 009 mantida).

## Nota

O TF odom -> base_link e a sincronização de relógio ficam para a questão seguinte. O TF costuma ser consumido com reliable, o que pode exigir QoS própria.