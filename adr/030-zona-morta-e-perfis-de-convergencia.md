---
data: 2026-10-23
status: provisório
camada: "controlador"
revoga:
revogada_por:
affects: []
evidence: [V-01, V-09]
---
# 030 – Zona morta abaixo de V_MIN e convergência com desaceleração constante

## Problema

Abaixo de V_MIN, o encoder lê velocidade zero. Com a referência em zero, o resíduo do integrador pode manter d > 0, e o robô desliza sem que o controlador perceba. Pela mesma razão, o TURN_TO e o GO_TO não conseguem convergir exatamente no alvo: param quando a referência das rodas cruza V_MIN.

## Decisão

- **Zona morta:** referência de uma roda abaixo de V_MIN leva a d = 0 (freio total) e zera o integrador dessa roda.
- **GO_TO:** v = min(v_max, √(2·a_dec·d)) · max(0, cos e). Aqui d é a distância ao alvo e e é o erro de ângulo até ele. O termo de correção angular continua com peso que vai a zero com a distância.
- **TURN_TO:** ω = sinal(e) · min(ω_max, √(2·α_dec·|e|)), com α_dec = 2·a_dec / b, onde b é a bitola.

## Erro final

O robô para quando a referência das rodas cruza V_MIN:

- GO_TO: d_final ≈ V_MIN² / (2·a_dec)
- TURN_TO: e_final ≈ V_MIN² / (b·a_dec)

Exemplo ilustrativo, com V_MIN = 0,068 m/s, a_dec = 0,5 m/s² e b = 0,15 m: d_final ≈ 5 mm e e_final ≈ 3,5°. O erro cai com a_dec maior e com bitola maior.

Esse erro se soma ao erro da odometria. A tolerância de término no sequenciador deve ser maior que ele.

## Alternativa descartada

- **Sem zona morta:** permite deslizamento não observado.
- **Perfil linear (v ∝ d):** com desaceleração limitada a a_dec, o ganho fica restrito a a_dec / v_max, e o erro final chega a centímetros (V_MIN · v_max / a_dec).
- **Comportamento PARAR (freio em malha aberta):** é a mesma função de transferência de TWIST(0, 0), e o freio sem controle desacelera as rodas de forma desigual.

## Racional

- Abaixo de V_MIN a velocidade não é observável, então controlá-la é impossível. O monitor de falha já ignora essa faixa.
- A regra depende da entrada (a referência), não de estado interno, e mantém o RNF-04.
- A desaceleração constante a_dec é a mais rápida sem escorregamento nem tensão reversa (ADR 023). Ela minimiza o erro final e não exige mais do que a rampa permite. Se exigisse, a rampa cortaria o perfil e o robô passaria do alvo.
- A parada mais rápida possível com controle é TWIST(0, 0) com a_dec.

## Nota

- Os perfis usam um a_dec um pouco abaixo do limite da rampa, como folga para a discretização em T_C.
- O erro final do TURN_TO, de alguns graus, é o maior efeito desta decisão e deve ser medido na V-01.
