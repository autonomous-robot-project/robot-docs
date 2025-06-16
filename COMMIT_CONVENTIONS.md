# Commit Conventions

Este repositório utiliza convenções de commit para manter clareza e rastreabilidade do conteúdo registrado em ciclos de trabalho. Um commit deve refletir com precisão a intenção da mudança.

## Tipos de Commit

Use os seguintes **tipos de commit** no início da mensagem:

- `log:` Para registros de execução de tarefas, testes, observações e ações feitas durante uma atividade prática.
- `write:` Para adição de conteúdo técnico original (documentação de sistemas, modelos, explicações).
- `revise:` Para alterações significativas em documentos técnicos existentes (correções, melhorias, reestruturações).
- `reflect:` Para anotações de reflexão, dúvidas, aprendizados, hipóteses ou considerações sobre o sistema ou o processo.
- `meta:` Para ações de infraestrutura do repositório (configurações, renomeações, organização interna, ajustes de estrutura).

## Exemplo

```
log: teste com kp = 0.8 e kd = 0.2 — oscilação reduzida
write: adição da seção de controle PID no sistema de locomoção
revise: reestruturação da documentação de mapeamento SLAM
reflect: questionamento sobre impacto da frequência de amostragem no PID
meta: reorganização da estrutura de pastas e arquivos
