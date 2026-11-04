---
data: 2026-10-28
status: provisório
camada: "controlador"
revoga:
revogada_por:
affects: [robot-firmware/components/controller]
evidence: [V-01, V-04]
---
# 048 – Odometria pela contagem de bordas

## Problema

A odometria precisa do deslocamento de cada roda em cada ciclo. A velocidade medida é zero abaixo de v_min (ADR 030), e na partida só existe depois de duas bordas.

## Decisão

Em cada ciclo, o deslocamento de cada roda é a diferença da contagem de bordas desde o ciclo anterior, vezes s, com o sentido travado da ADR 019. A pose integra Δs = (Δl + Δr)/2 e Δθ = (Δr − Δl)/L_rodas no ponto médio. A velocidade publicada sai das velocidades medidas.

## Alternativa descartada

- **Velocidade medida × T_c:** perde as fendas da partida e as abaixo de v_min, ~1 a 2 fendas (10 a 20 mm) por partida e parada, até 40 % de ε_d na V-01. A estimativa s/Δt só aproxima a distância entre bordas.

## Racional

- Cada fenda é um deslocamento medido de s. Contá-la é a medida mais direta que o encoder dá.
- O único erro que resta é o do canal único, uma fenda por inversão, já aceito na ADR 019. A transformação map → odom o corrige como qualquer deriva.
- A pose é estado de estimação, admitido por Gat como filtragem. O controlador a usa nos comportamentos e a publica, mas não decide sobre ela (RNF-04).

## Nota

A pose é calculada na tarefa de controle e publicada pela tarefa micro-ROS a 20 Hz, com o instante local da pose convertido para o relógio do agente (ADR 027).
