---
data: 2026-10-23
status: provisório
camada: "controlador"
revoga:
revogada_por:
affects: []
evidence: [V-05, V-08, V-09]
---
# 028 – Instrumentação como opção de build e prazo perdido como falha

## Problema

A V-05 precisa medir C_max, R_max e prazos perdidos. Essas medidas são ferramenta de verificação, não estado do robô. Mesmo assim, uma perda de prazo em operação precisa ser conhecida, já que a V-05 limita a probabilidade de perda, mas não a anula.

## Decisão

- A instrumentação é uma opção de build (Kconfig). Ligada, mede no `controlador` e publica pelo `enlace`. Desligada, não existe no binário de produção.
- A perda de prazo é detectada em todos os builds e publicada como código de falha no estado. O código fica ativo por tempo limitado após a última perda. Não há reflexo associado.

## Alternativa descartada

- **Instrumentação sempre presente:** mistura ferramenta de verificação com o produto, sem ganho de validade.
- **Instrumentação como componente separado:** os pontos de medida ficam dentro do ciclo, e o controlador passaria a depender de um componente opcional.
- **Prazo perdido só na instrumentação:** a falha passaria despercebida em produção.
- **Reflexo para prazo perdido:** nenhuma ação local restaura o tempo do laço.

## Racional

- A instrumentação só acrescenta tempo ao ciclo. As medidas com ela são limite superior das medidas sem ela, então a V-05 vale para o build de produção.
- Detectar a perda de prazo custa quase nada, porque a tarefa já conhece t_k. É falha cognizante, como pede Gat: a perda é detectada e reportada, e o sequenciador decide.
- Manter o código ativo por tempo limitado garante que o sequenciador o veja, e mantém o estado efêmero (RNF-02).

## Nota

A duração do código ativo será fixada junto com a escada de recuperação do sequenciador.
