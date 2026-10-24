---
data: 2026-10-23
status: provisório
camada: "controlador"
revoga:
revogada_por:
affects: []
evidence: [V-01, V-09]
---
# 024 – Três comportamentos primitivos, selecionados por mensagem própria

## Problema

O RF-01 e o RF-04 exigem um conjunto de comportamentos primitivos selecionados pelo sequenciador. Com um único comportamento de velocidade, o término do GIRAR ficaria a cargo do sequenciador em escala de T_SEQ, o que daria vários graus de erro. Isso deixaria uma malha de realimentação contínua morando fora do controlador.

## Decisão

O controlador tem três comportamentos, cada um controlando uma grandeza:

| Comportamento | Grandeza | Parâmetros |
| --- | --- | --- |
| VELOCIDADE | Velocidade linear e angular | (v, ω) |
| GIRAR | Posição angular | θ |
| IR_PARA | Posição linear | (x, y) |

O comando é uma mensagem própria, com o comportamento ativo e seus parâmetros. θ e (x, y) são dados no referencial da odometria.

O término é sempre do sequenciador. O controlador converge, restringe por reflexos e reporta, mas nunca troca de comportamento sozinho.

## Alternativa descartada

- **Só Twist (um comportamento):** a precisão do giro ficaria limitada por T_SEQ, e o conjunto do RF-01 se reduziria a um elemento.
- **Twist com tópico de modo separado:** o comportamento e os parâmetros chegariam separados e poderiam ficar inconsistentes, cada um com o seu vencimento.
- **Fila de comportamentos no controlador:** exigiria decidir o término no controlador, o que contradiz o RNF-04 e a ADR 017. A continuidade já é garantida pela rampa da ADR 023.

## Racional

- Para Gat, um comportamento é uma função de transferência. Os três fecham malhas diferentes sobre os encoders. O controle de posição exige o laço de 10 ms, não T_SEQ.
- Gat cita "mover-se até um destino" como primitivo clássico. O Alfred usava seguimento de rumo com o término por posição no sequenciador.
- Uma pose completa (x, y, θ) não admite realimentação contínua estática em robô diferencial (Brockett, 1983). Por isso a pose é composta pelo sequenciador a partir de GIRAR e IR_PARA.
- Esta ADR define os comportamentos que compõem a sequência da ADR 015: GIRAR(θ do vértice) e depois IR_PARA(vértice).
- Uma mensagem só mantém o comando atômico: uma caixa de correio e um vencimento (ADR 017, RNF-02). Coerente com a ADR 012.

## Nota

- **GIRAR:** o sequenciador nunca comanda θ a 180° ou mais do rumo atual, para evitar a descontinuidade do erro de ângulo.
- **IR_PARA:** a saída deve tender a (0, 0) com a distância ao alvo, para ser contínua em todo lugar (RNF-04).
- **Manter distância sobre o VL53L0X:** fica como issue no `robot-docs`, vinculada à escada de recuperação do sequenciador.
