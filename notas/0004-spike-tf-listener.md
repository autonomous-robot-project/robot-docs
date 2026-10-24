# Spike #23: TransformListener sem thread própria (rclpy, Jazzy) - 2026-10-24 - sem commit de código

Montagem:
- Só RPi 5 (Jazzy). Nó rclpy com `SingleThreadedExecutor`, `TransformListener(buffer, node)` e
  timer de 20 Hz com `lookup_transform('odom', 'map', Time())`, 200 consultas por cenário.
- Cenários: (a) map → odom estático (`static_transform_publisher`, como no ensaio);
  (b) map → odom dinâmico a 20 Hz, de outro processo, no lugar do SLAM; (c) sem publicador.
- Scripts descartáveis em `~/spike23` no RPi.

Código-fonte (`tf2_ros` do Jazzy):
- `spin_thread` é `False` por padrão. As assinaturas de `/tf` e `/tf_static` são criadas no próprio nó
  (`ReentrantCallbackGroup`) e atendidas pelo executor dele. A thread só existe com `spin_thread=True`.
- `lookup_transform` com o timeout padrão (zero) chama `can_transform` sem laço de espera.
  Com timeout > 0, `can_transform` faz um laço com `sleep(0.02)`.

Medido:

| Cenário | Threads (Python, SO) antes → depois | Consultas ok / exceção | Consulta: mediana / máx. | Período do timer: mediana / máx. |
|---|---|---|---|---|
| (a) estático | (1, 15) → (1, 15) | 199 / 1 | 71 µs / 168 µs | 50,00 ms / 50,18 ms |
| (b) dinâmico | (1, 15) → (1, 15) | 192 / 8 | 81 µs / 134 µs | 50,00 ms / 50,03 ms |
| (c) sem publicador | (1, 15) → (1, 15) | 0 / 200 | 65 µs / 137 µs | 50,00 ms / 50,09 ms |

- Nenhuma thread nova, nem Python nem do SO. A consulta custa < 0,2 ms, inclusive quando falha.
- No (b), cada consulta viu um map → odom novo (192 valores distintos).
- As exceções do (a) e do (b) são só as primeiras consultas, antes da descoberta do publicador
  (até ~0,4 s depois de o nó subir). No (c), `LookupException` imediata em todas.

Ajustes:
- ADR 035: confirmado. Regra: a consulta usa timeout zero.

Surpresas:
- Com timeout > 0 num executor de uma thread, o laço de espera bloqueia o nó, e o `/tf` aguardado
  não é processado durante a espera: a espera nunca ajudaria.

Pendências:
- TF ausente nos primeiros ~0,4 s depois de o nó subir. A conversão só ocorre depois da resposta do
  planner, então não deve abortar a missão por isso: conferir na V-04.
