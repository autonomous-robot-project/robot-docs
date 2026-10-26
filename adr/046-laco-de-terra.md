---
data: 2026-10-25
status: provisório
camada: "controlador"
revoga:
revogada_por:
affects: []
evidence: []
---
# 046 – Laço de terra entre a bateria, o RPi e os drivers

## Problema

O RPi 5 é alimentado pela bateria por um buck síncrono, e o ESP32-S3 pela USB do RPi (ADR 044). O negativo da bateria chega ao GND do ESP32 por dois caminhos: pelo buck e pela USB, e pelo GND do DRV8871 e pelo fio de GND de sinal. Parte da corrente dos motores volta pelo segundo caminho. Isso deve ser aceito ou o laço deve ser quebrado?

## Decisão

- O laço é aceito.
- O GND de potência dos drivers e o negativo do buck vão em borne parafusado, com fio grosso, até um ponto único no negativo da bateria.
- Os pares de potência são trançados, para a corrente de PWM voltar pelo próprio par.
- A continuidade desse ponto é conferida antes de ligar.

## Alternativa descartada

- **Isolador digital nos IN1/IN2 (SI8641ED):** quebra o laço, mas acrescenta um componente e a alimentação do lado isolado para eliminar uma oscilação estimada em ~5 mV.
- **Sem o GND de sinal no driver:** o retorno de IN1/IN2 passaria pelo buck e pela USB, num laço maior.

## Racional

- RF-03 e RNF-02: o reflexo e a parada dependem de os IN1/IN2 serem lidos corretamente. A oscilação estimada (~5 mV, com ~10 % da corrente de pico no laço) fica duas ordens abaixo do V_IL do DRV8871 (0,5 V).
- O risco real é perder o retorno de potência, porque aí toda a corrente do motor passa pelo fio de 24 AWG e pela USB. O borne e a checagem de continuidade cobrem esse caso.

## Nota

Estimativa resistiva sem medição. As bordas do PWM podem gerar picos maiores. Se aparecerem no ADC do divisor ou nos encoders, a primeira medida é aproximar o ponto único dos drivers.
