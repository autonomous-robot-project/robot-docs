# Referência efetiva: só na Instrumentação, e só se uma medição pedir

A referência efetiva (depois de comando, vencimento, reflexos e rampa) não é publicada.
Nenhum consumidor precisa dela hoje:

- O sequenciador decide pelo resultado. A Odometria diz o que o robô fez, o eco do comando
  diz o que foi pedido e as máscaras dizem por que os dois diferem (reflexo ou falha).
- A V-03 verifica o RF-03 pelo efeito nos atuadores (comando mantido, reflexo ativo,
  velocidade medida a zero), não pela restrição interna.
- A V-08 herda os critérios da V-03, V-05 e V-07, e nenhum deles a usa.

Onde ela seria útil: nas medições de bancada de a_acel e a_dec (ADR 023) e na sintonia do PI.
Comparar a referência depois da rampa com a velocidade medida é o que caracteriza a malha.

Ao escrever o procedimento dessas medições:

- Se a medição exigir a referência efetiva, ela entra na Instrumentação, que só existe no
  build de verificação (ADR 028). Não entra no Estado (ADR 025, critério para dados novos).
- Se a medição puder ser feita com o comando e a Odometria, ela continua sem ser publicada.
