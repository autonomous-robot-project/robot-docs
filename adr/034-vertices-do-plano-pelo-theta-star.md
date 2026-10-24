---
data: 2026-10-24
status: provisório
camada: "sequenciador / deliberador"
revoga:
revogada_por:
affects: []
evidence: [V-04, V-09]
---
# 034 – Vértices do plano pelo Theta*

## Problema

O sequenciador emite um par TURN_TO → GO_TO por trecho do plano (ADRs 015 e 024), então precisa de uma poligonal de vértices. O `planner_server` do Nav2 devolve um caminho denso, com um ponto por célula do costmap. Quem transforma o caminho em vértices, sem trazer computação deliberativa ao sequenciador (RNF-03)?

## Decisão

- O sequenciador consulta o `planner_server` pela action `ComputePathToPose`, de forma assíncrona (ADRs 014 e 033).
- O planner é o Theta*, que escolhe os vértices por linha de visada sobre o costmap e interpola entre eles na resolução do mapa.
- O sequenciador recupera os vértices como os pontos do caminho onde a direção muda, numa passada linear. O plano não é alterado, só a representação.

## Alternativa descartada

- **Douglas-Peucker no sequenciador:** muda a geometria do plano dentro do sequenciador, com desvio de até ε_s não verificado contra o costmap.
- **Douglas-Peucker num nó do deliberador:** mantém a fronteira, mas acrescenta um nó e um salto de action para fazer o que o Theta* já faz.
- **Caminho denso como vértices:** um par TURN_TO → GO_TO por célula, com centenas de paradas. Reprova a V-04.

## Racional

- RF-07: o deliberador fornece o plano e o sequenciador só o converte em comportamentos. A geometria de cada trecho é decidida no deliberador.
- Gat: busca e verificação de colisão ficam no deliberador; a passada sobre o caminho não é busca nem projeção temporal (RNF-03).
- Cada trecho é livre de colisão por construção, porque é a própria linha de visada do Theta*.

## Nota

- Resposta de uma meta antiga é descartada pelo identificador da meta; no aborto da missão, a meta pendente é cancelada.
- Erro do planner, caminho vazio ou action server ausente são falhas da missão, tratadas pela tabela de reações (ADR 032). As missões de ensaio não consultam o deliberador (RF-05).
- O caminho vem em `map`; a conversão para `odom` é decisão à parte.
- O tratamento do último ponto da interpolação e a tolerância numérica da colinearidade devem ser conferidos no `Path` gravado na V-04.
