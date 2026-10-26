# Cabeamento e leitura de bateria

## Conexões (breakout do ESP32-S3 com header dupont macho e bornes)

- **Sinais:** terminal dupont fêmea crimpado em carcaça 1x2, 1x3 ou 1x4. A carcaça dá trava mecânica. JST-XH descartado, porque o lado da placa é dupont.
- **Potência (motores, VM, bateria):** fica nos bornes parafusados, fora das espirais de sinal.
- **Fio:** 0,20 mm² (≈24 AWG), multifilar, 10 cores, 3 m por cor. O kit de terminais aceita 18-26 AWG.
- **Proteção:** espiral de 6 mm (5 m). Um chicote por dispositivo, com carcaça nas duas pontas e espiral começando ~1 cm depois dela. A exceção é juntar os 2 encoders ou os 2 drivers, se o trajeto for parecido.
- **Fixação:** abraçadeira de nylon a cada 10 a 15 cm, sem apertar.

## Mapa de pinos (ESP32-S3-DevKitC-1 N16R8, CP2102)

Um lado para os fios ruidosos e outro para os sensíveis, cada chicote saindo junto ao seu GND.
O breakout dá GND em dupont e borne: 2 + 1 embaixo à esquerda, 1 + 1 em cima à direita e 2 + 2 embaixo à direita.
O 3V3 só existe em cima à esquerda.

Lado esquerdo (ruidoso: PWM dos drivers):

| GPIO | Função | GND |
|---|---|---|
| 11 / 12 | DRV8871 esquerdo IN1 / IN2 | dupont de baixo, 1 |
| 13 / 14 | DRV8871 direito IN1 / IN2 | dupont de baixo, 2 |
| 10 | Reservado para o buzzer | definido quando ele entrar |

Lado direito (sensível e enlace):

| GPIO | Função | GND | VCC |
|---|---|---|---|
| 1 | Divisor da bateria (ADC1_CH0) | dupont de cima | — |
| 42 / 41 | UART1 TX / RX (enlace, ADR 043) | borne de cima | — |
| 40 / 39 | I²C SDA / SCL (VL53L0X) | dupont de baixo, 1 | 3V3 |
| 47 / 21 | Encoder esquerdo / direito | dupont de baixo, 2, e borne de baixo | 3V3 |
| 38 | Injeção de laço infinito na tarefa de controle (V-02): nível baixo trava a tarefa | encostado no GND só no ensaio | — |

- Os encoders vão em 3V3, para a saída chegar ao ESP32 em 3,3 V.
- O ESP32-S3 é alimentado pela USB do RPi 5.
- Os pinos de JTAG (39 a 42) servem para o enlace e o I²C: no S3, o JTAG padrão vai pela USB, e o estado desses pinos no reset não importa para eles.
- Só os drivers dependem do estado no reset. O DRV8871 tem pull-down interno de 100 kΩ em IN1/IN2 (ADR 008), e a #21 confirma o nível baixo no reset e na gravação.

Fora do mapa: strapping (0, 3, 45, 46), flash e PSRAM octal (26 a 37), USB nativa (19, 20), UART0 do CP2102 (43, 44) e LED RGB da placa (48).

Livres: 2 (separa o divisor do enlace), 4 a 9 e 15 a 18. GND livres: borne de baixo à esquerda e um borne de baixo à direita.

## Chicotes

| Dispositivo | Vias | Sinais |
|---|---|---|
| VL53L0X | 4 | VCC, GND, SDA, SCL (XSHUT e GPIO1 não usados) |
| Encoder (x2) | 3 | VCC, GND, sinal |
| DRV8871 (x2) | 3 | GND, IN1, IN2 |
| Buzzer passivo | 3 | VCC, sinal, GND |
| Divisor da bateria | 2 | sinal, GND |
| Enlace UART (RPi GPIO 14/15 ↔ ESP32-S3 GPIO 42/41) | 3 | TX, RX, GND (cruzados: TX de um no RX do outro) |

## Padrão de cores (igual em todos os chicotes)

Preto = GND, vermelho = VCC, amarelo = sinal principal (encoder, IN1, buzzer), verde = sinal secundário (IN2, SDA), azul = SCL. Lado esquerdo em branco e direito em laranja, se precisar distinguir.

O preto é o único com folga curta: ~7 GND, com 3 m disponíveis. Meça os trechos antes de cortar.

## Regras de roteamento

- I2C curto (≤ 20-30 cm), sozinho, longe de motor e VM.
- Encoders longe dos fios de motor.
- Encoder e driver nunca na mesma espiral.
- GND comum entre ESP32, drivers e divisor.
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
- Alimente o divisor depois da chave principal, para não drenar a bateria desligada (~220 µA).
- Faça a leitura com os motores parados ou com média, porque o PWM dos motores perturba o ADC.

## Verificação antes de ligar

1. Teste de puxão em 3 ou 4 crimpagens antes dos chicotes reais.
2. Continuidade de cada fio, ponta a ponta, sem curto entre vizinhos.
3. Medir a saída do divisor com o multímetro antes de ligá-lo ao pino do ADC. Com a bateria cheia deve dar ~2,2 V.
