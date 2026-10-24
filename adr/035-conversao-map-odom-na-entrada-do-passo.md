---
data: 2026-10-24
status: provisório
camada: "sequenciador"
revoga:
revogada_por:
affects: []
evidence: [V-04]
---
# 035 – Conversão map → odom na entrada do passo

## Problema

Os vértices do plano chegam em `map` (ADR 034), e os alvos do TURN_TO e do GO_TO são dados em `odom` (ADR 024). A odometria deriva, e a correção do SLAM aparece no TF map → odom. Quando o sequenciador converte cada vértice, e como lê esse TF?

## Decisão

- O vértice é convertido para `odom` na entrada de cada passo, com o map → odom mais recente, como parte do cálculo dos parâmetros (ADR 032). Durante o passo, o alvo fica fixo.
- O TF é lido por um buffer do `tf2_ros` no executor do próprio nó (ADR 033), com consulta sem espera.

## Alternativa descartada

- **Converter o plano inteiro ao recebê-lo:** a deriva agiria sem correção durante a missão toda.
- **Reconverter a cada republicação:** os saltos do alvo a cada correção do SLAM fariam o término oscilar perto da zona morta (ADR 030).
- **Listener com thread própria:** contradiz a ADR 033.
- **Compor map → odom a partir da pose do SLAM e da Odometria:** reimplementa o que o TF já entrega.

## Racional

- Gat: a pose odométrica é estado de filtragem no controlador. O estado de mundo (vértices em `map`) fica no sequenciador, e a deriva só age por um passo, porque cada passo reancora o alvo.
- O resíduo de um passo é corrigido pelo seguinte, como o do TURN_TO já é corrigido pelo GO_TO.
- RNF-03: a consulta ao buffer não espera e tem tempo constante.
- Gat admite que o deliberador forneça resultados por consulta ou de forma contínua. O map → odom do SLAM é um resultado contínuo lido sob demanda; o plano continua por consulta (ADR 014).

## Nota

- As missões de ensaio usam alvos em `odom`, sem TF (RF-05).
- Missão por plano sem map → odom disponível é falha da missão, tratada pela tabela de reações (ADR 032).
- Com as rodas suspensas (V-04), o launch publica um map → odom estático e identidade.
- Confirmado no Jazzy (issue #23, nota 0004): o TransformListener do rclpy não cria thread por padrão, e a consulta custa < 0,2 ms. A consulta usa timeout zero: com timeout > 0, a espera bloquearia o executor, que é quem processa o `/tf`.
