# V-02 - Cálculo da medição de velocidade e de v_min

## Dados

| Símbolo | Significado | Valor |
| :---: | :---: | :---: |
| D | Diâmetro da roda | 65 mm |
| N | Pulsos por volta (bordas de subida, canal único) | 20 |
| v_r | Velocidade comandada no ensaio | 0,2 m/s |
| e_f | Limiar de erro relativo para falha | 50 % |
| T_f | Persistência do erro para detectar falha | 300 ms (estimativa) |
| T_c | Período do laço de controle | 10 ms |

## Passo 1 - Deslocamento por pulso

A roda percorre uma circunferência por volta e gera N pulsos nessa volta:

$$C = \pi D = \pi \cdot 0{,}065 = 0{,}2042\ \text{m}$$

$$s = \frac{C}{N} = \frac{0{,}2042}{20} = 0{,}0102\ \text{m} \approx 10{,}2\ \text{mm}$$

## Passo 2 - Frequência de pulsos na velocidade do ensaio

$$f = \frac{v_r}{s} = \frac{0{,}2}{0{,}0102} \approx 19{,}6\ \text{pulsos/s}$$

$$\Delta t = \frac{s}{v_r} = \frac{0{,}0102}{0{,}2} \approx 51\ \text{ms}$$

## Passo 3 - Inviabilidade da contagem de pulsos por período

Pulsos esperados em um período de controle:

$$\frac{v_r \, T_c}{s} = \frac{0{,}2 \cdot 0{,}01}{0{,}0102} \approx 0{,}2\ \text{pulsos}$$

Resolução de velocidade por contagem (um pulso por período):

$$\Delta v = \frac{s}{T_c} = \frac{0{,}0102}{0{,}01} \approx 1{,}02\ \text{m/s}$$

A resolução é cerca de cinco vezes maior que a própria referência. A contagem por período é descartada.

## Passo 4 - Medição pelo intervalo entre pulsos

A ISR do encoder registra o instante de cada borda de subida, e a velocidade é obtida por:

$$v = \frac{s}{\Delta t}$$

A resolução passa a ser a do timer (µs), desprezível frente a Δt ≈ 51 ms. Usa-se apenas a borda de subida, porque fendas e barras do disco não têm larguras iguais e contar as duas bordas introduziria jitter.

## Passo 5 - Estimativa com a roda travada

Sem pulsos, Δt não se fecha. Decorrido um tempo t desde o último pulso, a roda percorreu menos que s, logo:

$$v_{real} < \frac{s}{t}$$

O controlador usa:

$$v_{est} = \min\left(\frac{s}{\Delta t_{último}},\ \frac{s}{t_{desde\ último}}\right)$$

Assim, a estimativa decai continuamente enquanto não chega pulso.

## Passo 6 - Instante em que a estimativa cruza o limiar

A falha ocorre quando a velocidade fica abaixo de:

$$v_{lim} = (1 - e_f)\, v_r = 0{,}5 \cdot 0{,}2 = 0{,}1\ \text{m/s}$$

Com a roda travada, a estimativa s/t atinge esse valor em:

$$t^* = \frac{s}{v_{lim}} = \frac{0{,}0102}{0{,}1} \approx 102\ \text{ms}$$

Este é o pior caso (travamento logo após um pulso). Se a roda travar perto do próximo pulso, o cruzamento ocorre antes, medido a partir do travamento.

## Passo 7 - Velocidade mínima de validade (v_min)

Exige-se que a espera do Passo 6 não exceda a persistência, t* ≤ T_f:

$$\frac{s}{(1 - e_f)\, v} \le T_f \quad\Rightarrow\quad v \ge \frac{s}{(1 - e_f)\, T_f}$$

$$v_{min} = \frac{s}{(1 - e_f)\, T_f} = \frac{0{,}0102}{0{,}5 \cdot 0{,}3} \approx 0{,}068\ \text{m/s}$$

Com e_f = 50 %, a expressão se reduz a 2s/T_f. A forma geral continua válida se e_f mudar.

Abaixo de v_min a medida já não é válida, então a velocidade é declarada zero após um intervalo sem bordas de:

$$T_{vel} = \frac{s}{v_{min}} = (1 - e_f)\, T_f = 0{,}5 \cdot 0{,}3 = 150\ \text{ms}$$

Verificação: v_r = 0,2 m/s > v_min = 0,068 m/s ✓

## Passo 8 - Latência total de detecção

$$t^* + T_f \approx 102 + 300 \approx 400\ \text{ms} < 1\ \text{s (duração do travamento)}\ ✓$$

## Passo 9 - Filtro de bordas espúrias

Módulos com comparador sem histerese (ex.: LM393) podem gerar bordas múltiplas na transição. Nenhuma borda real chega antes do intervalo correspondente à velocidade máxima:

$$\Delta t_{min} = \frac{s}{v_{max}}$$

A ISR descarta bordas mais próximas que Δt_min, com margem. Exemplo: com v_max = 0,5 m/s, Δt_min ≈ 20 ms.

## Atualização após medição

Os Passos 1 a 6 dependem apenas da roda e do encoder. Quando o tempo de acomodação for medido e T_f fixado (T_f = 2 × tempo de acomodação), refazem-se apenas os Passos 7 e 8 (incluindo T_vel).

## Limitações

- **Sentido de rotação:** o encoder de canal único não mede sentido. O sinal da velocidade é tomado do comando.
- **Taxa de realimentação:** a 0,2 m/s a medida atualiza a ~20 Hz, o que limita a banda do laço de velocidade e tende a aumentar o tempo de acomodação, e com ele T_f e v_min.
