---
data: 2026-10-23
status: provisório
camada: "controlador"
revoga:
revogada_por:
affects: []
evidence: [V-09]
---
# 029 – Watchdog de tarefas sobre a tarefa de controle

## Problema

Se a tarefa de controle travar, o PWM fica no último duty e o reflexo frontal deixa de agir, porque mora na mesma tarefa. Uma tarefa travada não detecta a própria trava. Os travamentos das outras tarefas já degradam de forma segura: o comando vence (RNF-02) e o sensor envelhece até a falha (ADR 021).

## Decisão

A tarefa de controle é inscrita no watchdog de tarefas do ESP-IDF, com prazo de poucos T_c. Ao estourar o prazo, o chip reinicia e o estado seguro dos drivers da ADR 008 assume.

Após um reinício por watchdog, o controlador publica o código de falha "reinício por watchdog", ativo por tempo limitado.

## Alternativa descartada

- **Watchdog sobre todas as tarefas:** reiniciaria o robô por travamentos que já degradam de forma segura.
- **Prazo padrão do ESP-IDF (segundos):** daria metros de movimento às cegas.

## Racional

- Cobre a única falha sem outra proteção: um defeito que trave a tarefa de controle. Pânicos já reiniciam o chip pelo tratador padrão.
- É falha cognizante, como pede Gat: um observador externo detecta a falha que a tarefa não detecta sozinha.
- Não acrescenta mecanismo: o watchdog de tarefas já está ativo por padrão; só se inscreve a tarefa e se encurta o prazo.
- O código de falha informa o sequenciador. A causa do reset é lida no boot, sem estado retido entre reinícios (RNF-02).

## Nota

O prazo e a duração do código ativo serão fixados em bancada.
