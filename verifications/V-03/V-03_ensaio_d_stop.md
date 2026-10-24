# Ensaio – Alcance do sensor, distância de parada e velocidade máxima

## Objetivo

Fixar d_stop e v_max a partir de duas medições: o alcance confiável do VL53L0X (d_sensor) e a distância de parada do robô (d_parada). As três distâncias devem obedecer a:

$$d_{parada}(v_{max}) + v_{max} \cdot T_S \le d_{stop} \le d_{sensor}$$

v_max é um resultado do ensaio, não um dado: o projeto não troca garantia por desempenho.

## Parâmetros

| Símbolo | Significado | Valor |
| :---: | :---: | :---: |
| d_sensor | Maior distância com leitura válida do VL53L0X na superfície de pior caso | medido (Parte A) |
| d_stop provisório | Limiar do reflexo durante a Parte B | = d_sensor |
| d_disparo | Leitura do VL53L0X na ativação do reflexo | medido |
| d_final | Leitura do VL53L0X com o robô parado | medido |
| v | Velocidade comandada em cada série da Parte B | crescente, até o limite do duty de 48 % |
| T_S | Tempo sem leitura classificável após o qual o reflexo declara falha (ADR 021) | a fixar por medição |

## Condições

- Piso de operação do robô.
- Parada pela rampa a_dec em decaimento lento (ADR 023).

## Parte A – Alcance do sensor (d_sensor)

1. Use as superfícies de pior caso: uma escura e fosca e uma espelhada ou brilhante.
2. Para cada superfície, afaste-a do sensor em passos de 5 cm, registrando o status e a distância lida (pelo menos 20 leituras por posição).
3. d_sensor é a maior distância em que todas as leituras têm status válido, nas duas superfícies.

## Parte B – Distância de parada (d_parada)

1. Configure d_stop = d_sensor.
2. Inicie a gravação com `ros2 bag` da distância do VL53L0X, da velocidade medida e do estado do reflexo.
3. Posicione o robô a 2 m ou mais de uma parede lisa e fosca, alinhado a ela, e comande VELOCIDADE(v, 0).
4. Aguarde o reflexo parar o robô.
5. Execute os passos 3 e 4 cinco vezes por velocidade, aumentando v a cada série.

## Cálculo

$$d_{parada} = d_{disparo} - d_{final}$$

- **v_max** é a maior v ensaiada com max(d_parada) + v·T_S + margem ≤ d_sensor, limitada também pela velocidade alcançada com duty de 48 %.
- **d_stop** = max(d_parada em v_max) + v_max·T_S + margem, com margem de 2 a 3 cm (exatidão do VL53L0X).

## Validade

- A velocidade medida no instante do disparo deve ser v (conferir no bag). Se o robô ainda estivesse acelerando, a distância sai subestimada.
- d_parada é medida a partir da leitura que disparou o reflexo (d_disparo), não do instante em que o obstáculo cruzou D_STOP. Até essa leitura chegar, o robô já avançou. v_max·T_S cobre essa diferença. O d_stop só fica fechado depois que T_S for fixado.
- A distância vem do VL53L0X, não do encoder (resolução de 10,2 mm por pulso e deslizamento na frenagem). Uma fita no chão serve de conferência.
- O resultado vale apenas para o a_dec e o piso registrados.
- Premissas da garantia: obstáculos estáticos que entram no campo do sensor além de d_parada. O campo é estreito (≈ 25°), então obstáculos laterais em curvas ou giros podem escapar.

## Notas – DRV8871

**Freio (IN1 = IN2 = alto)**, o duty zero do decaimento lento, aplicado abaixo de V_MIN (ADR 030):

- Os MOSFETs de baixo curto-circuitam o motor, e a força contraeletromotriz gera torque de frenagem proporcional à velocidade. A distância de parada é menor e depende menos do piso que no modo livre.
- A corrente de frenagem não passa da corrente de stall (1,2 A), porque a força contraeletromotriz não passa da tensão de alimentação. Fica abaixo do limite do DRV8871.
- A corrente recircula pelos MOSFETs de baixo, sem devolver energia ao VM.
- O modo livre (IN1 = IN2 = baixo) foi descartado: além da parada mais longa, o driver entra em sono após ~1 ms nesse estado, acrescentando tempo de despertar na retomada.

**PWM em decaimento lento:**

- Para frente: IN1 = alto e PWM invertido em IN2. No sentido contrário, troca-se IN1 e IN2.
- No intervalo desligado do PWM, o motor fica em freio. A velocidade varia de forma quase linear com o duty, o que melhora o controle em baixa velocidade, útil com a realimentação lenta do encoder (~20 Hz a 0,2 m/s).
- No ESP32, a inversão é feita pela opção de saída invertida do LEDC, sem inverter o duty no código.
