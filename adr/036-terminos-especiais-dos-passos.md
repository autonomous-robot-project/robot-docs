---
data: 2026-10-24
status: provisório
camada: "sequenciador"
revoga:
revogada_por:
affects: []
evidence: [V-01, V-04]
---
# 036 – Términos especiais dos passos

## Problema

Os términos padrão (TURN_TO: |e_θ| ≤ ε_θ em repouso; GO_TO: d ≤ ε_d em repouso) não cobrem dois casos. Um alvo de giro a 180° ou mais do rumo atual é proibido pela ADR 024. Um robô em repouso fora da tolerância não é sucesso nem borda de falha, e o passo ficaria parado.

## Decisão

- **Giro grande:** com |Δθ| > θ_max, o TURN_TO comanda θ_atual ± θ_max. Ao parar nesse alvo parcial, reentra no passo, e o `heading_to` recalculado já fica abaixo de θ_max.
- **Sem progresso:** repouso fora da tolerância, depois de ter havido movimento no passo, gera o evento `NO_PROGRESS`, do próprio sequenciador. Ele é tratado na tabela de reações (ADR 032), com o aborto como padrão.

## Alternativa descartada

- **Giro grande como falha da missão:** o robô não alcançaria alvos atrás dele.
- **Confiar no controlador em 180°:** o sinal do erro fica ambíguo, contra a ADR 024.
- **Tempo máximo por passo:** depende de a_acel e v_max ainda não medidos.
- **Reentrada automática sem progresso:** política fixa fora da tabela, com risco de laço.

## Racional

- ADR 024: nenhum comando de giro chega a 180°, e a divisão usa a reentrada que já existe (ADR 032).
- RF-04: parar antes do alvo é um resultado do passo e precisa levar a uma escolha. Na tabela, a missão escolhe abortar ou tentar de novo.
- A condição "depois de ter havido movimento" evita o falso evento na entrada, quando o robô já está em repouso, sem constante nova.

## Nota

- O TURN_TO é emitido mesmo com o robô alinhado: termina na primeira Odometria, e a V-04 continua contando pares TURN_TO → GO_TO.
- θ_max é parâmetro, com margem sobre a resolução da odometria (≈ 4,5° por pulso); ponto de partida 170°.
- O robô que nunca se mexe, sem falha nem reflexo, fica para os monitores do eco e do enlace.
