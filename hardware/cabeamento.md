# Cabeamento e leitura de bateria

## Conexões (breakout do ESP32-S3 com header dupont macho e bornes)

- **Sinais:** terminal dupont fêmea crimpado em carcaça 1x2, 1x3 ou 1x4. A carcaça dá trava mecânica. JST-XH descartado, porque o lado da placa é dupont.
- **Potência (motores, VM, bateria):** fica nos bornes parafusados, fora das espirais de sinal.
- **Fio:** 0,20 mm² (≈24 AWG), multifilar, 10 cores, 3 m por cor. O kit de terminais aceita 18-26 AWG.
- **Proteção:** espiral de 6 mm (5 m). Um chicote por dispositivo, com carcaça nas duas pontas e espiral começando ~1 cm depois dela. A exceção é juntar os 2 encoders ou os 2 drivers, se o trajeto for parecido.
- **Fixação:** abraçadeira de nylon a cada 10 a 15 cm, sem apertar.

## Mapa de pinos (ESP32-S3-DevKitC-1 N16R8, CP2102)

Cada roda fica no seu lado da placa: a direita no header do TX/RX (J3) e a esquerda no do 3V3 (J1).
O driver fica na metade de cima e o encoder embaixo, perto da USB, ligado pelo borne.
O breakout dá GND em dupont e borne: 2 + 1 embaixo à esquerda, 1 + 1 em cima à direita e 2 + 2 embaixo à direita.
O 3V3 só existe em cima à esquerda.

Lado esquerdo (J1, roda esquerda):

| GPIO | Função | GND |
|---|---|---|
| 4 / 5 | DRV8871 esquerdo IN1 / IN2 | dupont de baixo |
| 10 | Reservado para o buzzer | definido quando ele entrar |
| 11 | Injeção de laço infinito na tarefa de controle (V-02): nível baixo trava a tarefa | encostado no GND só no ensaio |
| 14 | Encoder esquerdo (borne) | borne de baixo |

Lado direito (J3, roda direita):

| GPIO | Função | GND | VCC |
|---|---|---|---|
| 1 | Divisor da bateria (ADC1_CH0) | dupont de baixo | — |
| 2 / 42 | DRV8871 direito IN1 / IN2 | dupont de cima | — |
| 41 / 40 | UART1 TX / RX (enlace, ADR 043; provisório, a rediscutir) | borne de cima | — |
| 39 / 38 | I²C SDA / SCL (VL53L0X) | dupont de baixo | 3V3 |
| 21 | Encoder direito (borne) | borne de baixo | 3V3 |

- Os encoders vão em 3V3, para a saída chegar ao ESP32 em 3,3 V.
- O ESP32-S3 é alimentado pela USB do RPi 5.
- Os pinos de JTAG (39 a 42) servem para o driver direito, o enlace e o I²C: no S3, o JTAG padrão vai pela USB, e o estado desses pinos no reset não importa para eles.
- O 1 e o 2 são os únicos ADC1 do header direito; o divisor fica com o 1.
- Só os drivers dependem do estado no reset. O DRV8871 tem pull-down interno de 100 kΩ em IN1/IN2 (ADR 008), e a #21 confirma o nível baixo no reset e na gravação.

Fora do mapa: strapping (0, 3, 45, 46), flash e PSRAM octal (26 a 37), USB nativa (19, 20: alimentação e gravação pelo RPi, ADR 044), UART0 do CP2102 (43, 44) e LED RGB da placa (48).

Livres: 6 a 9, 12, 13, 15 a 18 e 47. GND livres: um dupont de baixo à esquerda e um borne de baixo à direita.

Chave dos motores: uma chave gangorra com LED (20 A) no VM dos dois DRV8871, depois do fusível. Ela desliga só os motores; o ESP32 segue alimentado pelo RPi. Na V-02, é ela que corta a alimentação (falha cognizante sem travar a roda). O ESP32 continua aplicando nível alto em IN1/IN2 com o VM cortado, o que o DRV8871 admite: "Safe to provide logic high signals without VM present" (datasheet, No-VM Behavior).

- Pinos da chave: prata do centro na entrada (+ depois do fusível), a outra prata na saída para o VM dos drivers e o dourado (terra do LED) no GND. "Ligado" é a posição em que as duas pratas fecham.
- Fusível geral (lâmina mini) no + da bateria, logo depois do XT30: 2 A na primeira energização (motores soltos); 5 A provisório com os motores, até a corrente de roda travada ser medida. Quando o RPi passar para a bateria, ele divide o mesmo fusível, e o valor é revisto. Até lá, o RPi fica na tomada.

## Chicotes

| Dispositivo | Vias | Sinais | Trança |
|---|---|---|---|
| VL53L0X | 4 | VCC, GND, SDA, SCL (XSHUT e GPIO1 não usados) | Nenhuma (SDA com SCL aumenta a diafonia) |
| Encoder (x2) | 3 | VCC, GND, sinal | Nenhuma (fio curto, encoder junto ao ESP32) |
| DRV8871 (x2) | 3 | GND, IN1, IN2 | Tripla IN1 + IN2 + GND |
| Buzzer passivo | 3 | VCC, sinal, GND | Nenhuma |
| Divisor da bateria | 2 | sinal, GND | Par sinal + GND |
| Enlace UART (RPi GPIO 14/15 ↔ ESP32-S3 GPIO 42/41) | 3 | TX, RX, GND (cruzados: TX de um no RX do outro) | Tripla TX + RX + GND |

## Padrão de cores (igual em todos os chicotes)

Preto = GND, vermelho = VCC, amarelo = sinal principal (encoder, IN1, buzzer), verde = sinal secundário (IN2, SDA), azul = SCL. Lado esquerdo em branco e direito em laranja, se precisar distinguir.

O preto é o único com folga curta: ~7 GND, com 3 m disponíveis. Meça os trechos antes de cortar.

## Regras de roteamento

- I2C curto (≤ 20-30 cm), sem trança, sozinho na espiral. Cruza fios de potência só a ~90°, nunca em paralelo.
- Fios de potência (OUT1/OUT2 de cada motor, VM/GND de cada driver) trançados em par.
- Encoders longe dos fios de motor.
- Encoder e driver nunca na mesma espiral.
- GND comum entre ESP32, drivers e divisor.
- O GND do divisor vai ao GND do ESP32, sem fio próprio até a bateria: um segundo retorno ao negativo faria a corrente do motor passar pelos fios de sinal se o negativo principal soltar (ADR 046).
- Bateria ligada por XT30, para o negativo não soltar durante um ensaio.
- GND de potência dos drivers e negativo do buck do RPi em borne parafusado, com fio grosso, num ponto único no negativo da bateria (ADR 046).
- Capacitor de bulk no VM de 47 µF / 50 V em cada módulo DRV8871.

## Leitura de bateria (3S Li-ion, 9,0 a 12,6 V)

```markdown
Bateria (+) ──[47k 1%]──┬──[1k]──┬── GPIO1 (ADC1_CH0)
                        │        │
                      [10k]   [100nF]
                        │        │
GND ────────────────────┴────────┴── GND
```

- Fator: V_bat = V_pino × 5,7. Em 12,6 V o pino vê 2,2 V, e em 9 V vê 1,58 V.
- Firmware: `analogReadMilliVolts()` com média de várias amostras. Ajuste o fator comparando com o multímetro.
- Use só pino ADC1 (o ADC2 não é utilizável no S3).
- O divisor fica sempre ligado: liga antes da chave dos motores, senão leria 0 V com eles desligados (~220 µA, ~15 meses para descarregar a bateria de 2500 mAh).
- Faça a leitura com os motores parados ou com média, porque o PWM dos motores perturba o ADC.

## Verificação antes de ligar

1. Teste de puxão em 3 ou 4 crimpagens antes dos chicotes reais.
2. Continuidade de cada fio, ponta a ponta, sem curto entre vizinhos.
3. Medir a saída do divisor com o multímetro antes de ligá-lo ao pino do ADC. Com a bateria cheia deve dar ~2,2 V.
4. Continuidade do GND de potência de cada driver e do negativo do buck até o ponto único na bateria (ADR 046).
