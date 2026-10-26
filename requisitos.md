# Requisitos

## Requisitos Funcionais

**RF-01 - Comportamentos primitivos.** O controlador deve implementar um conjunto de comportamentos primitivos, cada um como uma função entre sensores e atuadores. O comportamento ativo e seus parâmetros são definidos em tempo de execução por entrada externa.
**Camada:** controlador. **Verificação:** ensaio (bancada), na mesma sessão do RF-04.

**RF-02 - Falha cognizante do controlador.** O controlador deve detectar e reportar ao sequenciador a incapacidade de executar o comportamento ativo.
**Camada:** controlador + interface com o sequenciador. **Verificação:** ensaio (bancada, rodas suspensas, corte da alimentação do motor de uma roda).

**RF-03 - Reflexo reativo do controlador.** O controlador deve restringir o comando dos atuadores em resposta direta a condições detectadas pelos sensores, independentemente do comando recebido e do estado das demais camadas.
**Camada:** controlador. **Verificação:** ensaio (bancada, com detecção de obstáculo como instância).

**RF-04 - Seleção condicional de comportamentos.** O sequenciador deve selecionar e parametrizar, em tempo de execução, o comportamento primitivo ativo no controlador (ex.: seguir velocidade, parar, girar no lugar), escolhendo o próximo com base no resultado (sucesso ou falha) do comportamento em execução.
**Camada:** sequenciador. **Verificação:** ensaio por sequência de comandos sob falhas.

**RF-05 - Autonomia do sequenciador.** O sequenciador deve selecionar comportamentos no controlador sem depender do deliberador, recorrendo a ele apenas para resultados que exijam computação deliberativa.
**Camada:** sequenciador. **Verificação:** ensaio (bancada, com os nós do deliberador desligados).

**RF-06 - Computação deliberativa.** O deliberador deve executar os algoritmos cujo tempo de execução é longo em relação à taxa de variação do ambiente, como os de planejamento e busca, e fornecer seus resultados ao sequenciador.
**Camada:** deliberador. **Verificação:** ensaio (bancada, planejamento sobre mapa gravado).

**Nota:** o controlador e o sequenciador têm restrições próprias em Gat, e o deliberador é definido por não ter. O peso da camada está na fronteira com o sequenciador.

**RF-07 - Integração das camadas.** Os resultados fornecidos pelo deliberador devem ser convertidos pelo sequenciador em comportamentos executados pelo controlador.
**Camada:** interface deliberador, sequenciador e controlador. **Verificação:** ensaio (bancada, cadeia completa deliberador, sequenciador e controlador).

## Requisitos Não Funcionais

**RNF-01 - Determinismo do laço de controle.** Cada iteração das tarefas de tempo real do controlador deve ter tempo de execução e uso de memória limitados, cumprindo seus prazos sob a carga de projeto.
**Camada:** controlador. **Verificação:** ensaio (bancada, análise estatística da medição) para o tempo; inspeção de código (alocação estática, sem alocação dinâmica no laço) para a memória.

**Nota:** justifica a decisão arquitetural central: por que a camada de controlador está em um MCU dedicado.

**RNF-02 - Estado interno efêmero.** Toda representação interna do mundo no controlador que não seja de filtragem deve vencer em tempo limitado. O último comando recebido deve vencer em tempo limitado, resultando no comportamento de parada.
**Camada:** controlador. **Verificação:** ensaio (bancada, com interrupção do publicador de comandos como instância).

**Nota:** o vencimento do comando é o mecanismo de estado efêmero exigido por Gat e não configura violação do RNF-04.

**RNF-03 - Limite temporal do sequenciador.** O sequenciador não deve executar busca nem planejamento, e seu tempo de reação a eventos do controlador, medido, deve ser inferior a T_seq.
**Camada:** sequenciador. **Verificação:** inspeção de código + ensaio.

**Nota:** o controlador tem prazo rígido, o deliberador não tem restrição e o sequenciador é rápido, mas sem garantia rígida. T_seq = 100 ms, um período de varredura do LiDAR: a informação nova mais rápida acima do controlador.

**RNF-04 - Continuidade dos comportamentos.** A saída de cada comportamento do controlador deve variar continuamente com seu estado interno; decisões baseadas em estado interno pertencem ao sequenciador.
**Camada:** controlador. **Verificação:** inspeção de código.

**RNF-05 - Isolamento temporal do deliberador.** Controlador e sequenciador devem continuar atendendo o RNF-01, o RNF-03 e o RF-03 enquanto o deliberador estiver computando ou sob sobrecarga do computador embarcado.
**Camada:** controlador e sequenciador. **Verificação:** ensaio.

## Verificações

| ID | Nome | Método | Requisitos |
| :---: | :---: | :---: | :---: |
| V-01 | Seleção de comportamentos | Ensaio | RF-01, RF-04, RF-05 |
| V-02 | Falha cognizante | Ensaio | RF-02 |
| V-03 | Reflexo reativo | Ensaio | RF-03 |
| V-04 | Integração das camadas | Ensaio | RF-06, RF-07 |
| V-05 | Cumprimento de prazos | Ensaio | RNF-01 |
| V-06 | Vencimento do comando | Ensaio | RNF-02 |
| V-07 | Reação do sequenciador | Ensaio | RNF-03 |
| V-08 | Isolamento temporal do deliberador | Ensaio | RNF-05 |
| V-09 | Inspeção de código e registros | Inspeção | RF-02, RF-03, RF-06, RF-07, RNF-01, RNF-02, RNF-03, RNF-04 |
