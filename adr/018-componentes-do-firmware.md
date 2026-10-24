---
data: 2026-10-23
status: provisório
camada: "controlador"
revoga:
revogada_por:
affects: []
evidence: [V-09]
---
# 018 - Firmware em dois componentes: controlador e enlace

## Problema

A parte de tempo real do controlador não deve depender da comunicação com o sequenciador. Em um único componente, essa fronteira dependeria só de disciplina e inspeção.

## Decisão

O firmware tem dois componentes ESP-IDF e um ponto de entrada:

- **controlador:** tarefa de tempo real, sensores, atuação e as caixas de correio (ADR 017). Não depende do micro-ROS.
- **enlace:** tarefa micro-ROS e conversão de mensagens. Depende do controlador, nunca o contrário.
- **main:** só inicializa os dois.

## Alternativa descartada

- **Componente único:** a independência do laço em relação ao micro-ROS ficaria só na inspeção.
- **Um componente por função:** fronteiras sem nenhuma propriedade exigida por trás.

## Racional

- O build passa a impor a separação entre o controlador e a interface com o sequenciador. Um uso do micro-ROS dentro do controlador vira erro de compilação, o que protege o RNF-01.
- A dependência segue a hierarquia de Gat: a camada de cima conhece a de baixo.
- O grafo de dependências declarado é evidência direta para a V-09, e o controlador pode ser ensaiado sem o enlace.

## Nota

A organização interna de cada componente é decisão de commit. Sugestão: separar a lógica pura do acesso ao hardware dentro do controlador.
