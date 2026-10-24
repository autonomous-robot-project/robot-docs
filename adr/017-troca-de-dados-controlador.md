---
data: 2026-10-23
status: provisório
camada: "controlador"
revoga:
revogada_por:
affects: []
evidence: [V-05, V-09]
---
# 017 - Troca de dados entre contextos do controlador por caixas de correio do FreeRTOS

## Problema

A ISR do encoder, a tarefa de controle e a tarefa micro-ROS rodam em núcleos diferentes e compartilham dados. A tarefa de controle não pode esperar por nenhum deles (RNF-01).

## Decisão

Cada fluxo de dados usa uma caixa de correio do FreeRTOS (fila de um elemento), alocada estaticamente e com um único produtor.

A implementação deve garantir:

- semântica de último valor;
- nenhuma operação bloqueante na tarefa de controle;
- caixa de comando vazia tratada como comando vencido;
- a caixa de comando carrega o instante de chegada, gravado pelo produtor; a tarefa de controle vence o comando pela idade.

## Alternativa descartada

- **Struct compartilhada com seção crítica própria:** mesmo efeito, com código de concorrência a justificar.
- **Buffer triplo lock-free:** sem ganho mensurável com T_C = 10 ms e de verificação mais difícil.

## Racional

- Gat exige iteração do controlador com tempo e memória limitados. Uma leitura sem espera de um valor de tamanho fixo cumpre isso (RNF-01).
- O controlador é reativo: precisa do valor mais recente, não do histórico. O histórico é do sequenciador.
- Tratar a caixa vazia como comando vencido reaproveita o estado efêmero do RNF-02, sem caso especial.
- O primitivo já existe no RTOS, o que é mais claro e mais simples de inspecionar (V-09) do que um mecanismo próprio.

## Nota

Pressupõe que todo dado trocado é de último valor. Condições são publicadas como estado atual
