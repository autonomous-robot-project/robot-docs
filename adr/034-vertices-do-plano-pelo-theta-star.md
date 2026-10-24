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
- O sequenciador recupera os vértices como os pontos do caminho onde a direção muda, numa passada linear, e trata as pontas e os trechos curtos:
  - descarta o primeiro ponto (centro da célula de partida), porque o primeiro trecho parte da pose atual;
  - troca o último ponto (centro da célula do objetivo) pelo objetivo pedido e remove o vértice vizinho dele, se houver;
  - absorve um trecho mais curto que 2·ε_g removendo um de seus vértices internos, se esse vértice ficar a até res/2 do novo segmento.
- O desvio do plano fica limitado a res/2, exceto na última célula, e é coberto pela célula extra da zona proibida (ADR 042).

## Alternativa descartada

- **Douglas-Peucker no sequenciador:** muda a geometria do plano dentro do sequenciador, com desvio de até ε_s não verificado contra o costmap. A absorção acima é mais restrita: só trechos curtos, com desvio limitado a res/2, que o costmap já cobre.
- **Douglas-Peucker num nó do deliberador:** mantém a fronteira, mas acrescenta um nó e um salto de action para fazer o que o Theta* já faz.
- **Caminho denso como vértices:** um par TURN_TO → GO_TO por célula, com centenas de paradas. Reprova a V-04.

## Racional

- RF-07: o deliberador fornece o plano e o sequenciador só o converte em comportamentos. A geometria de cada trecho é decidida no deliberador.
- Gat: busca e verificação de colisão ficam no deliberador; a passada sobre o caminho não é busca nem projeção temporal (RNF-03).
- Cada trecho é livre de colisão por construção, porque é a própria linha de visada do Theta*, e a célula extra da zona proibida cobre o desvio da passada (ADR 042).
- Na grade, o Theta* contorna a zona proibida com facetas de uma célula e chega ao objetivo por uma célula vizinha. Sem o tratamento, cada faceta seria um par TURN_TO → GO_TO de poucos centímetros.

## Nota

- Resposta de uma meta antiga é descartada pelo identificador da meta; no aborto da missão, a meta pendente é cancelada.
- Erro do planner, caminho vazio ou action server ausente são falhas da missão, tratadas pela tabela de reações (ADR 032). As missões de ensaio não consultam o deliberador (RF-05).
- O caminho vem em `map`; a conversão para `odom` é decisão à parte.
- Conferido num `Path` real (issue #24, nota 0003): com peso de travessia mínimo, os pontos interpolados são colineares, e a extração não depende da tolerância (de 1e-9 a 0,1 rad). O caminho começa e termina em centros de célula.
