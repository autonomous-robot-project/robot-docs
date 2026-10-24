# Destacar: GO_TO é comportamento emergente

O GO_TO não tem lógica de código: nenhum `if`, nenhum estado de "girando" ou "andando".
É uma única lei de realimentação, avaliada a cada 10 ms sobre a pose atual:
  v ∝ d · max(0, cos e),   ω ∝ e · (peso -> 0 quando d -> 0)
O comportamento observado (girar no lugar, fazer um arco, andar reto e desacelerar no alvo)
não é programado; ele emerge da equação.

Pontos para a banca:

- A trajetória não é planejada: ela resulta da lei aplicada à pose de cada instante.
- Isso é robusto: um desvio é corrigido no ciclo seguinte, sem replanejar.
- A equação é contínua em todo lugar (RNF-04). A pose completa (x, y, θ) não poderia
  ser tratada assim (Brockett, 1983); por isso a composição é feita pelo sequenciador.
- Liga-se à tese de Gat: primitivas simples, compostas por um sequenciador, produzem
  comportamento complexo.
