---
data: 2026-10-26
status: provisório
camada: "controlador"
revoga:
revogada_por:
affects: []
evidence: [V-03, V-05, V-09]
---
# 023 – Anti-windup e limite de duty, sem rampa na referência

## Problema

Variações bruscas de referência podem causar picos de corrente na bateria, e o integrador do PI acumula erro durante a saturação, por exemplo com a roda travada ou com um reflexo ativo, o que provoca um tranco na liberação. Como limitar esses efeitos?

## Decisão

- Sem rampa na referência: o transiente é o da malha fechada. O PI tem o zero no polo do motor, então a malha de velocidade é de 1ª ordem, sem sobressinal, com tempo de acomodação t_s de projeto.
- O duty fica limitado a 48 %.
- O integrador não acumula enquanto a saída está saturada e o erro a empurra para mais saturação.
- O monitor de falha compara a velocidade medida com a referência da roda (RF-02).
- A frenagem é o próprio PWM em decaimento lento; o freio total é o caso de duty igual a zero.

## Alternativa descartada

- **Rampa assimétrica na referência (versão anterior desta ADR):** limita a aceleração com dois parâmetros (a_acel e a_dec), mas o transiente já é dado pela malha fechada. Seriam dois mecanismos para o mesmo efeito.
- **Limite de variação do duty, depois do PI:** fica dentro da malha, causa windup e altera a dinâmica sintonizada.

## Racional

- Com t_s = 0,5 s, um degrau de 0,2 m/s pede duty de 0,11 a 0,14, sem saturar, e o erro cai abaixo de e_f em τ_mf · ln 2 ≈ 87 ms, muito antes de T_f.
- Com duty ≤ 48 %, a roda travada recebe no máximo a tensão nominal do motor, o que limita a corrente.
- Frear em decaimento lento faz a corrente circular no motor, sem sair da bateria. A passagem do controle para o freio é contínua (RNF-04), sem troca de modo.
- A integração condicional mantém o integrador limitado, de acordo com a regra de Gat de que o estado interno não deve guardar crença sem limite.

## Nota

- Sem rampa, TWIST(0, 0) é o freio total (ADR 030), e a parada segue a constante de tempo de frenagem do motor, τ_freio, medida na caracterização.
- O freio total gera estresse mecânico e térmico considerável no conjunto motor e redutor. Todo ensaio com freio total começa em velocidade baixa, para ver como o motor se comporta, e só depois sobe a velocidade.
- Os números valem com a roda suspensa. No chão a inércia é maior: o motor será caracterizado de novo com o robô no chão. Se a aceleração inicial (Δv / τ_mf) causar escorregamento ou pico de corrente, a rampa volta.
