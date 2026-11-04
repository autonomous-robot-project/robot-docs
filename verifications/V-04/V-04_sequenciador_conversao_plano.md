# Sequenciador - Conversão do plano em comportamentos

## Funcionamento

O deliberador entrega um plano como uma sequência fixa de vértices. O sequenciador não recalcula o plano. No início de cada trecho, ele calcula o rumo da pose odométrica atual (x, y) até o próximo vértice (x_v, y_v):

$$\theta_{alvo} = \operatorname{atan2}(y_v - y,\ x_v - x)$$

Em seguida, ativa TURN_TO(θ_alvo) e depois GO_TO(x_v, y_v). O GO_TO recebe o próprio vértice, e a distância até ele é calculada pelo controlador. Após o último vértice, ativa TWIST(0, 0).

## Por que partir da pose atual

O GO_TO vai ao próprio vértice, então o erro de posição não se acumula em nenhum dos casos. Partir da pose atual faz o TURN_TO apontar para o vértice, e não para a direção do trecho no plano, e deixa ao GO_TO só o resíduo do TURN_TO.

## Conformidade com a arquitetura

- **RNF-03:** sem busca nem planejamento. É uma operação de tempo constante por trecho.
- **Gat (1998):** o sequenciador usa estado interno (pose e índice do vértice atual) sem busca nem projeção temporal.
- **RNF-04:** a decisão de término (|e_θ| ≤ ε_θ e d ≤ ε_d, com a odometria em repouso) fica no sequenciador, e não no controlador.

## Consequência na V-04

Como nenhum trecho propaga erro até o objetivo:

$$\varepsilon_g = \varepsilon_d$$
