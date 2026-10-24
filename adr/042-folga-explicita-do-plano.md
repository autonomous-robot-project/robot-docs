---
data: 2026-10-24
status: provisório
camada: "deliberador"
revoga:
revogada_por:
affects: []
evidence: [V-04]
---
# 042 – Folga explícita do plano

## Problema

Cada trecho do plano é executado em linha reta, sem seguimento de caminho (ADR 015). O desvio lateral vem do erro de odometria acumulado no passo. Como o plano garante uma folga dos obstáculos que cubra esse desvio?

## Decisão

- O planner proíbe as células a menos de raio do robô + margem m de um obstáculo.
- O custo de travessia tem peso mínimo, e o Theta* faz o caminho mais curto fora da zona proibida.

## Alternativa descartada

- **Folga pelo gradiente de custo:** o planner prefere o meio do espaço livre. A folga fica implícita em pesos sem significado físico, e o plano ganha vértices e paradas.
- **Pesos padrão do planner:** a mesma folga implícita, sem justificativa a partir dos requisitos.

## Racional

- RF-06: a folga faz parte da verificação de colisão, que fica no deliberador. Cada trecho é livre de colisão por construção, já com a margem (ADR 034).
- Menos vértices dão menos paradas e trechos mais longos, como pressupõe a V-04.

## Nota

- Ponto de partida: m = 0,10 m. O valor depende do desvio lateral no chão e não entra em nenhuma verificação, que é feita em bancada.
- O planner pode atravessar espaço desconhecido: com o mapeamento contínuo (ADR 040), o objetivo pode estar em área ainda não mapeada, e o `replan()` corrige quando a área é observada.
