---
data: 2026-10-23
status: provisório
camada: "controlador"
revoga:
revogada_por:
affects: [robot-firmware/components/controller]
evidence: [V-01, V-09]
---
# 030 – Zona morta abaixo de v_min e convergência com desaceleração constante

## Problema

Abaixo de v_min, o encoder lê velocidade zero. Com a referência em zero, o resíduo do integrador pode manter d > 0, e o robô desliza sem que o controlador perceba. Pela mesma razão, o TURN_TO e o GO_TO não conseguem convergir exatamente no alvo: param quando a referência das rodas cruza v_min.

## Decisão

- **Zona morta:** referência de uma roda abaixo de v_min leva a d = 0 (freio total) e zera o integrador dessa roda.
- **GO_TO:** v = min(v_max, √(2·a_dec·e_d)) · max(0, cos e_θ) e ω = K_ω · sin e_θ · min(1, e_d/d₀), limitado a ω_max. Aqui e_d é a distância ao alvo e e_θ é o erro de ângulo até a direção dele.
- **TURN_TO:** ω = sinal(e_θ) · min(ω_max, √(2·α_dec·|e_θ|)), com α_dec = 2·a_dec / b, onde b é a bitola, e e_θ = θ comandado − rumo atual, normalizado em (−π, π].

## Erro final

O robô para quando a referência das rodas cruza v_min:

- GO_TO: e_d final ≈ v_min² / (2·a_dec)
- TURN_TO: e_θ final ≈ v_min² / (b·a_dec)

Exemplo ilustrativo, com v_min = 0,068 m/s, a_dec = 0,5 m/s² e b = 0,15 m: e_d final ≈ 5 mm e e_θ final ≈ 3,5°. O erro cai com a_dec maior e com bitola maior.

Esse erro se soma ao erro da odometria. A tolerância de término no sequenciador deve ser maior que ele.

## Alternativa descartada

- **Sem zona morta:** permite deslizamento não observado.
- **Perfil linear (v ∝ e_d):** com desaceleração limitada a a_dec, o ganho fica restrito a a_dec / v_max, e o erro final chega a centímetros (v_min · v_max / a_dec).
- **Correção angular do GO_TO pelo perfil do TURN_TO:** o ganho é infinito em e_θ = 0, e o rumo oscila em linha reta (1° já dá ±36 mm/s entre as rodas).
- **Correção angular do GO_TO crescente até 180° (e_θ linear ou 2·sin(e_θ/2)):** uma lei contínua e ímpar no círculo vale zero em ±π, então a lei crescente salta ali. O sin e_θ perde força acima de 90°, onde cos e_θ já zera v e o peso da distância já encolhe ω.
- **Comportamento PARAR (freio em malha aberta):** é a mesma função de transferência de TWIST(0, 0), e o freio sem controle desacelera as rodas de forma desigual.

## Racional

- Abaixo de v_min a velocidade não é observável, então controlá-la é impossível. O monitor de falha já ignora essa faixa.
- A regra depende da entrada (a referência), não de estado interno, e mantém o RNF-04.
- A desaceleração constante a_dec é a mais rápida sem escorregamento nem tensão reversa (ADR 023). Ela minimiza o erro final e não exige mais do que a rampa permite. Se exigisse, a rampa cortaria o perfil e o robô passaria do alvo.
- A parada mais rápida possível com controle é TWIST(0, 0) com a_dec.

## Nota

- Os perfis usam um a_dec um pouco abaixo do limite da rampa, como folga para a discretização em T_c.
- O erro final do TURN_TO, de alguns graus, é o maior efeito desta decisão e deve ser medido na V-01.
- No GO_TO, e_θ entra só por sin e cos, então vale em qualquer volta de θ. No TURN_TO, e_θ entra linear e por isso é normalizado: o comando vale em qualquer volta, e a única restrição é a da ADR 024.
- Valores iniciais: K_ω = 1 s⁻¹ (rumo com constante de tempo de 1 s, o dobro da acomodação da roda), d₀ = 0,1 m (2·ε_d), v_max = 0,2 m/s (a velocidade dos ensaios) e ω_max = 2·v_max/b (a roda não passa de v_max girando no lugar). v_max é provisório até a garantia de parada no chão (#27).
