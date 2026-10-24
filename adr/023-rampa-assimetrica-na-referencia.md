---
data: 2026-10-23
status: provisório
camada: "controlador"
revoga:
revogada_por:
affects: []
evidence: [V-03, V-05, V-09]
---
# 023 – Rampa assimétrica na referência efetiva, com anti-windup

## Problema

Variações bruscas de referência causam picos de corrente na bateria. O integrador do PI acumula erro durante a saturação, por exemplo com a roda travada ou com um reflexo ativo, e provoca um tranco na liberação.

## Decisão

- A aceleração é limitada sobre a referência efetiva (depois do comando, dos reflexos e do vencimento) e antes do PI.
- A rampa é assimétrica: a_acel é limitada pela corrente; a_dec, mais íngreme, é limitada pelo escorregamento e pela ausência de tensão reversa com a roda em movimento.
- O integrador só acumula enquanto a saída não está saturada.
- O monitor de falha compara a velocidade medida com a referência da roda depois da rampa, para que a aceleração limitada não seja lida como falha (RF-02).
- A frenagem é o próprio PWM em decaimento lento; o freio total é o caso de duty igual a zero.

## Alternativa descartada

- **Limite de variação do duty, depois do PI:** fica dentro da malha, causa windup e altera a dinâmica sintonizada.
- **Limites na referência e no duty:** dois mecanismos e dois parâmetros para o mesmo efeito.
- **Rampa simétrica:** submete a parada a uma restrição que só vale para a aceleração.

## Racional

- Um único ponto por onde passam todas as fontes de mudança. O PI recebe referência suave e a malha continua linear.
- Frear em decaimento lento faz a corrente circular no motor, sem sair da bateria, e ela fica limitada à corrente de partida. A passagem do controle para o freio é contínua (RNF-04), sem troca de modo.
- Com duty ≤ 48 %, a roda travada recebe no máximo a tensão nominal do motor.
- A integração condicional mantém o integrador limitado, de acordo com a regra de Gat de que o estado interno não deve guardar crença sem limite.

## Nota

a_dec entra na garantia de parada: d_parada ≈ v_max² / (2 · a_dec) + latências. a_acel e a_dec serão fixados por medição.
