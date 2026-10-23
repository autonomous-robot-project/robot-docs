# Cabeamento e leitura de bateria

## Conexões (breakout do ESP32-S3 com header dupont macho e bornes)

- **Sinais:** terminal dupont fêmea crimpado em carcaça 1x2, 1x3 ou 1x4. A carcaça dá trava mecânica. JST-XH descartado, porque o lado da placa é dupont.
- **Potência (motores, VM, bateria):** fica nos bornes parafusados, fora das espirais de sinal.
- **Fio:** 0,20 mm² (≈24 AWG), multifilar, 10 cores, 3 m por cor. O kit de terminais aceita 18-26 AWG.
- **Proteção:** espiral de 6 mm (5 m). Um chicote por dispositivo, com carcaça nas duas pontas e espiral começando ~1 cm depois dela. A exceção é juntar os 2 encoders ou os 2 drivers, se o trajeto for parecido.
- **Fixação:** abraçadeira de nylon a cada 10 a 15 cm, sem apertar.

## Chicotes

| Dispositivo | Vias | Sinais |
|---|---|---|
| VL53L0X | 4 | VCC, GND, SDA, SCL (XSHUT e GPIO1 não usados) |
| Encoder (x2) | 3 | VCC, GND, sinal |
| DRV8871 (x2) | 3 | GND, IN1, IN2 |
| Buzzer passivo | 3 | VCC, sinal, GND |
| Divisor da bateria | 2 | sinal, GND |

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

```
Bateria (+) ──[47k 1%]──┬──[1k]──┬── ADC1 (GPIO1-10)
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
