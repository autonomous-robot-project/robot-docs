# Fatia 1, passos 2 a 5: controller, troca com o link e V-06 - 2026-10-25 - commit 40e2f88 (robot-firmware)

Montagem: a mesma da nota 0005. Sem motores: a parada é observada no eco do Estado.

Medido:

| O quê | Resultado |
|---|---|
| State | 100 Hz, intervalo máximo ~10,5 ms |
| Ocupação do enlace, ESP32 → RPi | 5,6 %; 5,9 % com a Instrumentação a 10 Hz (orçamento 50 %) |
| Ocupação do enlace, RPi → ESP32 | 1,0 %, com o comando a 20 Hz |
| Overhead do XRCE sobre os dados | ~41 % (ESP32 → RPi), ~61 % (RPi → ESP32) |
| Latência comando → eco no State | 3,8 a 8,8 ms (bag) |
| V-06, 30 interrupções (`evidencias/V-06/2026-10-25_1849`) | PASS: 1 vencimento por interrupção, atraso no ESP32 de 200,0 a 209,8 ms |

Histórico dos ensaios da V-06:
1. Vencimentos de 212,7 a 212,9 ms (bag), travados em fase: o link olhava a UART a cada 10 ms, então o
   comando chegava ao controller até 10 ms depois da recepção. Corrigido com a entrega na chegada (0cba6c5).
2. 206,4 a 213,8 ms pelo bag. O bag soma enlace e fase do State, então nenhum limite fixo sobre ele prova o
   RNF-02: o atraso passou a ser medido no ESP32 (Instrumentação, ADR 028).
3. 3 interrupções, atraso no ESP32 de 201,0 a 205,9 ms. PASS, mas 3 amostras cobrem pouco da fase.
4. 30 interrupções, com o ciclo no instante nominal t_k (40e2f88): PASS (tabela acima).

Surpresas:
- O `ros2 topic pub` às vezes pausa 348 a 384 ms logo após a primeira mensagem (5 de 30 partidas; #40).
  O controlador venceu o comando nessas lacunas também (atrasos de 201 a 204 ms). O `-w 2` não evita a pausa.
  Sem `-w`, uma partida não publicou em 3 s.
- Defeito: `rcl_*_fini` chamado dentro do argumento de um `ESP_LOGD`, que some abaixo do nível de log
  (corrigido em 8bee846). O clang-tidy não pega efeito colateral em argumento de macro de log; o
  `check_link` com reinício do agente pegou.
- Falsa pista: a FIFO da UART não era a causa da fase travada do 1º ensaio.
- Uma reconexão depois de reiniciar o agente levou 3,1 s no `check_link` (antes, 0,6 s; #39).
