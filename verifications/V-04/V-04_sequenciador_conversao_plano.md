# Sequenciador - Conversão do plano em comportamentos

## Funcionamento

O deliberador entrega um plano como uma sequência fixa de vértices. O sequenciador não recalcula o plano. No início de cada trecho, ele calcula o giro e a distância da pose odométrica atual (x, y) até o próximo vértice (x_v, y_v):

$$\theta_{alvo} = \operatorname{atan2}(y_v - y,\ x_v - x)$$

$$d = \sqrt{(x_v - x)^2 + (y_v - y)^2}$$

Em seguida, ativa GIRAR até θ_alvo e SEGUIR por d. Após o último vértice, ativa PARAR.

## Por que partir da pose atual

| | Partida no vértice anterior do plano | Partida na odometria atual |
| :---: | :---: | :---: |
| Contas | atan2 e hipotenusa, uma vez por trecho | atan2 e hipotenusa, uma vez por trecho |
| Erro de cada trecho | Soma-se ao dos anteriores | É corrigido pelo trecho seguinte |
| Erro no objetivo | Cresce com o número de trechos | Só o do último trecho |

O custo é o mesmo. Muda apenas a origem de (x, y).

## Conformidade com a arquitetura

- **RNF-03:** sem busca nem planejamento. São duas operações de tempo constante por trecho.
- **Gat (1998):** o sequenciador usa estado interno (pose e índice do vértice atual) sem busca nem projeção temporal.
- **RNF-04:** a decisão de término (Δθ ≥ alvo, distância ≥ d) fica no sequenciador, e não no controlador.

## Consequência no V-04

Como só o último trecho propaga erro até o objetivo:

$$\varepsilon_g \ge e_d + L_{último} \cdot e_\theta$$
