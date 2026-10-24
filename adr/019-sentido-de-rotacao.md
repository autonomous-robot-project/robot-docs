---
data: 2026-10-23
status: provisório
camada: "controlador"
revoga:
revogada_por:
affects: []
evidence: [V-01, V-09]
---
# 019 – Sentido de rotação travado até a parada da roda

## Problema

O encoder de canal único mede o deslocamento, mas não o sentido. O sinal da velocidade é usado pelo PI, pela odometria e pelo monitor de falha.

## Decisão

O sentido de cada roda fica travado enquanto ela gira. Ele só é reavaliado quando a roda é dada como parada (sem borda por T_VEL) e, nesse momento, passa a seguir o sentido da tensão aplicada.

A estimação é feita na tarefa de controle. A ISR só registra instante e contagem de bordas.

## Alternativa descartada

- **Sinal da referência:** erra a cada inversão de referência e quando o reflexo ou o vencimento alteram a referência.
- **Sinal da tensão aplicada:** erra em toda frenagem, porque a roda gira para um lado enquanto o PI aplica tensão no sentido oposto.
- **Híbrido com limiar acima de V_MIN:** acrescenta a faixa de erro da frenagem e um parâmetro, sem reduzir o pior caso.
- **Encoder de quadratura:** muda o hardware fixado.

## Racional

- Um motor com inércia não inverte sem passar por zero, então travar o sentido enquanto a roda gira é fisicamente correto.
- O erro é limitado a uma fenda (≈ 10 mm) por inversão, que é a ambiguidade inerente ao canal único. A transformação map -> odom corrige esse erro como qualquer deriva.
- O sentido travado é estado de estimação, admitido por Gat como filtragem. É efêmero, porque se renova a cada parada, e não introduz descontinuidade na saída dos comportamentos (RNF-04).

## Nota

Na parada, a decisão coincide com a tensão aplicada, então esta ADR já incorpora a informação da alternativa anterior nesse regime.
