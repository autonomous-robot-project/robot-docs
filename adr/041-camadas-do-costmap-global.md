---
data: 2026-10-24
status: provisório
camada: "deliberador"
revoga:
revogada_por:
affects: []
evidence: [V-04]
---
# 041 – Camadas do costmap global

## Problema

O planner considera obstáculo o que estiver no costmap global. O `replan()` da escada de recuperação (ADR 038) é pedido com o robô parado diante de um obstáculo novo. Como esse obstáculo chega ao costmap a tempo de o plano novo desviar dele?

## Decisão

- Três camadas: a estática, com o mapa do SLAM (ADR 040); a de obstáculo, que marca e limpa o que o LiDAR vê a cada varredura; e a de inflação.
- O VL53L0X fica fora do costmap.

## Alternativa descartada

- **Só estática e inflação:** o SLAM só incorpora varreduras depois de um deslocamento mínimo. Com o robô parado, o mapa não muda, e o `replan()` devolveria o mesmo caminho bloqueado.
- **VL53L0X numa camada de alcance:** o sensor está no controlador e só sai como máscara de reflexo (ADR 025). Exigiria um tópico novo do controlador para um caso que o reflexo já cobre (RF-03).

## Racional

- RF-06: o obstáculo atual entra no plano pelo deliberador, que é quem verifica colisão. O sequenciador só pede o plano de novo (ADR 038).
- RNF-05: a camada de obstáculo fica no escalonador comum, com o resto do deliberador (ADR 039).

## Nota

- Obstáculo abaixo do plano do LiDAR, visto só pelo VL53L0X, não entra no plano novo, e a escada termina em aborto (ADR 038).
- A resolução é a mesma do mapa (0,05 m).
- O raio de inflação fica acima do raio do robô.
