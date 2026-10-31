---
data: 2026-10-25
status: provisório
camada: "controlador"
revoga:
revogada_por:
affects: [robot-firmware/components/controller, robot-firmware/components/link]
evidence: [V-05, V-06, V-08, V-09]
---
# 028 – Instrumentação sempre presente e prazo perdido como falha

## Problema

As verificações precisam de medidas internas do controlador: C_max, R_max e prazos perdidos (V-05) e o atraso do vencimento do comando (V-06). Essas medidas são ferramenta de verificação, não estado do robô. Mesmo assim, uma perda de prazo em operação precisa ser conhecida, já que a V-05 limita a probabilidade de perda, mas não a anula.

## Decisão

- A instrumentação existe em todos os builds. Ela mede no `controller` e publica pelo `link`, com valores acumulados desde o boot.
- A perda de prazo é publicada como código de falha no estado. O código fica ativo por tempo limitado após a última perda. Não há reflexo associado.

## Alternativa descartada

- **Instrumentação como opção de build:** o binário verificado deixaria de ser o que opera, e o código passaria a ter duas versões.
- **Instrumentação efêmera, só com o intervalo desde a mensagem anterior:** com best effort (ADR 025), uma mensagem perdida apagaria uma medida sem que a análise percebesse.
- **Instrumentação como componente separado:** os pontos de medida ficam dentro do ciclo, e o controlador passaria a depender de um componente opcional.
- **Prazo perdido só na instrumentação:** a falha passaria despercebida se ninguém estivesse gravando o tópico.
- **Reflexo para prazo perdido:** nenhuma ação local restaura o tempo do laço.

## Racional

- As verificações medem o mesmo binário que opera.
- A instrumentação é escrita pelo ciclo e nunca lida pelo controle. Ela registra a história do controlador, não uma representação do mundo, então fica fora do RNF-02. Ela custa tempo constante por ciclo e não aloca memória (RNF-01), e a própria V-05 mede esse custo.
- Valores acumulados toleram mensagens perdidas: a próxima traz tudo.
- Detectar a perda de prazo custa quase nada, porque a tarefa já conhece t_k. É falha cognizante, como pede Gat: a perda é detectada e reportada, e o sequenciador decide.
- Manter o código ativo por tempo limitado garante que o sequenciador o veja.

## Nota

A duração do código ativo é 200 ms após a última perda, reiniciada a cada nova perda: o dobro do mínimo da ADR 037; a escada (ADR 038) a ignora. Conferida por teste de host.
