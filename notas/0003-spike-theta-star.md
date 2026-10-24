# Spike #24: vértices do Theta* num Path real - 2026-10-24 - sem commit de código

Montagem:
- Só RPi 5 (Jazzy, Nav2 1.3.13): `map_server` com M, `planner_server` com Theta*, costmap global
  só com as camadas estática e de inflação (sem `/scan`), map → odom → base_link estáticos e identidade.
- `ComputePathToPose` de p₀ = (0, 0) a p_g = (2, 2), `/plan` gravado em bag, análise offline.
- Scripts descartáveis em `~/spike24` no RPi; refazer no robot-ros-system na fatia da V-04.

Medido:
- Célula segura no Theta*: custo ≤ 252. A inscrita (253) é proibida, então `robot_radius` = zona proibida.
- Colinearidade exata com `w_traversal_cost` = 0: mesmos vértices de 1e-9 a 0,1 rad.
  Com o padrão (2,0), o gradiente cria vértices de 3° a 7°.
- O Path começa e termina em centros de célula: (−0,025; −0,025) e (1,975; 1,975), a 0,035 m de p_g.
- Penúltimo vértice bruto sempre vizinho da célula do objetivo (trecho de 0,05 ou 0,071 m).
- Com zona r + m, a linha de visada invade células proibidas: ponto a 0,206 m com r + m = 0,23 m.
- Com zona r + m + res, 0 amostras a menos de r + m em 11 rodadas; folga mínima de 0,242 m.
- Vizinhança 8: faceta de uma célula diagonal (0,071 m) na quina, em 10 de 10 posições de parede.
- Resolução 0,025 m: folga 0,231 m, mas 5 trechos em vez de 3 e 4× células.
- M final (parede x 0,5–0,6, y −0,5–1,5; r = 0,131 m; zona 0,281 m), com a passada da ADR 034:
  trechos 1,697 · 0,292 · 0,150 · 1,337 m; giros +80,7° · −49,7° · −31,0° · +7,5°; folga 0,254 m.
  Figura: 0003-mapa-m.png.

Ajustes:
- ADR 034: pontas (primeiro ponto descartado, último trocado por p_g com o vizinho removido)
  e absorção de trecho < 2·ε_g com desvio ≤ res/2. Desvio medido de 0,014 a 0,021 m em 10 paredes.
- ADR 042: zona = r + m + res. Exceção na última célula (folga ≥ ≈ 0,21 m).
- V-04: M fixado. Resolução mantida em 0,05 m (ADR 041).

Surpresas:
- `kill -INT` não encerra processos em segundo plano em shell não interativo (SIGINT herdado ignorado):
  usar SIGTERM. O `ros2 launch` encerrado por SIGTERM deixou os nós filhos vivos.
- Theta* com vizinhança 4 dá poligonal limpa, mas presa aos eixos e com giro final de 2,8°.

Pendências:
- Giro de 7,5° no M final, perto da resolução de 4,5° por pulso da odometria: conferir na V-04.
- #25: raio medido (0,131 m); faltam bitola e pose do LiDAR.
