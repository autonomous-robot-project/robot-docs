---
data: 2026-10-24
status: provisório
camada: "deliberador"
revoga:
revogada_por:
affects: []
evidence: [V-04, V-08]
---
# 040 – SLAM em mapeamento contínuo

## Problema

O planner precisa de um mapa, e o sequenciador precisa do map → odom (ADR 035). Em operação, esses resultados vêm de um SLAM mapeando ao vivo ou de um mapa gravado com localização sobre ele?

## Decisão

- Em operação, o SLAM mapeia continuamente e publica o mapa e o map → odom. O planner planeja sobre esse mapa.
- Mapa gravado só nos ensaios (mapa M da V-04), servido por um servidor de mapa.

## Alternativa descartada

- **Mapear e depois localizar com o próprio SLAM:** exige um mapa serializado no formato do SLAM, além da imagem. Também cria duas fontes de mapa que precisam coincidir, e o M sintético não tem esse formato.
- **Mapear e depois localizar com filtro de partículas:** acrescenta uma fase, um nó e a pose inicial a cada sessão. A V-08 C1 pede o SLAM ativo.

## Racional

- RF-06: o requisito é planejar sobre mapa gravado, e a V-04 cumpre isso com o M servido diretamente. Localização sobre mapa prévio não é requisito.
- Gat: o mapa e o map → odom são resultados contínuos do deliberador, e o plano continua por consulta (ADRs 014 e 035).
- Cada `replan()` (ADR 038) planeja sobre o mapa mais recente.

## Nota

- Pacote: `slam_toolbox`, o SLAM de referência do Nav2.
- O SLAM fica no escalonador comum (ADR 039). Se atrasar, descarta varreduras e o mapa piora, mas o sequenciador não é afetado.
- Sem relocalização entre sessões: cada sessão começa um mapa novo, com a origem na pose inicial.
- Ensaios (V-04 e V-08 C1): o planner usa o M, e o map → odom é identidade e estático (ADR 035). Na V-08 C1, o SLAM roda com frame e tópico próprios, que ninguém consome, só como carga. Assim, toda consulta parte de p₀ em M e é um planejamento completo e repetível.
