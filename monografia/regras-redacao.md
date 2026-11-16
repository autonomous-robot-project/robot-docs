# Regras de redação da monografia

Checklist para escrever e revisar a monografia (robot-thesis). Cada regra cita a fonte. As regras mensuráveis
(tamanho de frase e parágrafo, pronomes, aspas, remissões vagas) são contadas por `medir_redacao.py`,
nesta pasta.

## Fontes

Os PDFs ficam em `referencias/`, fora do git, como o de Gat (1998).

| Sigla | Fonte | Arquivo | Base normativa |
| --- | --- | --- | --- |
| [P] | PRODANOV, C. C.; FREITAS, E. C. Metodologia do trabalho científico. 2. ed. Novo Hamburgo: Feevale, 2013. Número = página. | `Prodanov2013_metodologia-do-trabalho-cientifico.pdf` | NBR 14724:2011, NBR 10520:2002 |
| [C] | Slides "Componentes do texto acadêmico", PTCC, Profa. Vanessa A. A. de Lima (UFSC Joinville). Número = slide do PDF. | `Lima-PTCC_componentes-do-texto-academico.pdf` | NBR 14724:2024, NBR 10520:2023 |
| [O] | Slides "Orientações para a escrita do texto acadêmico", mesma disciplina. | `Lima-PTCC_orientacoes-para-a-escrita.pdf` | idem |
| [I] | Slides "Introdução ao PTCC", mesma disciplina. | `Lima-PTCC_introducao-a-disciplina.pdf` | idem |

Ordem das fontes (decisão do Lucas, 15/11/2026): orientadora > recursos do pré-TCC (slides e livro) > memórias do
projeto. O que a orientadora pede ou escreve nas correções prevalece sobre os slides e o livro. Entre os recursos do
pré-TCC:

- **Norma e apresentação** (citação, tabela, quadro, figura, sigla): ABNT vigente e o template > slides > livro. O livro
  segue normas já substituídas. Exemplo: a NBR 10520:2023 escreve "(Milani, 2010)", e não "(MILANI, 2010)".
- **Método** (classificação da pesquisa, problema, hipótese, objetivos): livro > slides.
- **Escolha da disciplina** (títulos do template, roteiro dos capítulos): slides, porque a professora avalia.

Normas usadas no TCC [I] 13: NBR 14724:2024 (trabalhos acadêmicos), 6024:2012 (numeração das seções), 6027:2013
(sumário), 6028:2021 (resumo), 10520:2023 (citações), 6023:2018 (referências).

## Pedidos da orientadora

[Or] marca o pedido da orientadora. Fonte: revisão do Cap. 3 em 15/11/2026, robot-thesis e0d8a9b. As correções dela
estão em roxo (`\tx{}`), com o texto antigo em `\sout{}`, e ficam no .tex até o Lucas mandar remover. O veredito
dela sobre o texto atual: as seções estão enormes, e o texto está prolixo, complexo, ruim de ler e em português
coloquial. O registro coloquial é o principal erro do trabalho. O alvo é o texto técnico e acadêmico, mas simples de
ler: o termo técnico dá a clareza, e não a frase complexa nem a palavra do dia a dia.

1. **Registro técnico e acadêmico, nunca coloquial.** A frase é técnica, mas não precisa ser complexa: o termo
   técnico exato dá clareza, e a palavra do dia a dia, não. Exemplos da revisão:

   | Coloquial (riscado) | Técnico (roxo) |
   | --- | --- |
   | A arquitetura aloca o controlador... | A arquitetura proposta neste trabalho distribui o controlador... |
   | O controlador ocupa o ESP32-S3 inteiro. | O controlador opera de maneira dedicada no ESP32-S3, sendo a única camada embarcada nesse microcontrolador. |
   | O sensor frontal tem uma tarefa própria porque a leitura é lenta e pode bloquear | Atribui-se uma tarefa exclusiva ao sensor frontal devido ao maior tempo de aquisição e ao caráter bloqueante de sua leitura |
   | Nenhum comportamento termina por conta própria. | As primitivas de comportamento não possuem critério interno de término |
   | A referência passa por uma rampa que limita a sua variação. | A referência de velocidade submete-se a um limitador de taxa de variação (*slew rate limiter*) |
   | ...para que a velocidade se acomode em 0,5 s sem sobressinal | ...garantindo resposta criticamente amortecida com tempo de acomodação de 0,5 s |
   | As condições vistas antes são esquecidas | O sequenciador descarta o histórico de condições anteriores |
   | O controlador não decide quando um comportamento termina. | O controlador não avalia condições de término de comportamento |
   | Gira no lugar até o rumo θ | Gira em seu eixo até o alvo θ |
   | O escopo do trabalho termina com... | O escopo do trabalho é finalizado com... |

   O padrão das correções:
   - o verbo do dia a dia (ficar, ter, passar, dar, vir, rodar, cair, esquecer, ocupar) vira o verbo técnico (operar,
     atribuir, submeter-se, descartar, compete a);
   - a descrição informal vira o nome do conceito ("sem sobressinal" → "criticamente amortecida"; "a roda
     dispara" → "realimentação positiva");
   - aparece a construção com "-se" ("Divide-se o *firmware*", "Executa-se o comando", "Observa-se");
   - o termo em inglês consagrado vai em itálico, junto do termo em português (*duty cycle*, *callback*, *thread*,
     *firmware*, *encoder*, *watchdog*, *publish-subscribe*);
   - na remissão a figura, aparece "Na Figura X, representam-se..." ou "A Figura X detalha...".
2. **Frases encadeadas, nunca frases soltas.** Um parágrafo não é uma lista de frases curtas com ponto final, como
   se fossem tópicos. As ideias se ligam por subordinação, aposto e conectivo no meio da frase. Exemplo reprovado
   (Cap. 3, abertura do planejamento dos testes):

   > Os Testes 1 a 4 verificam o que cada camada faz. O Teste 1 verifica a seleção de comportamentos pelo
   > Sequenciador. Os Testes 2 e 3 verificam a detecção de falhas e o reflexo do Controlador, que dispensam as
   > camadas superiores. O Teste 4 verifica a integração das três camadas [...].

   Na forma da orientadora, a mesma enumeração vira uma frase só: "Este trabalho adota três desses métodos: o
   ensaio, que...; a inspeção, que...; e a análise, que...".
3. **Concisão e leitura fácil.** As seções estão enormes e o texto, prolixo e complexo. Cada seção é encurtada,
   cada parágrafo tem uma ideia e cada frase diz uma coisa com o termo técnico exato, sem rodeio. Ao corrigir, a orientadora
   dividiu parágrafos com duas ideias (o limite do *encoder* e o sentido de giro) e cortou o que repetia outra seção.
4. **Toda tabela tem linha preta entre todas as linhas**, com `\hline` (sugestão dela). Sem as linhas, ela
   considerou a tabela ilegível.

## Processo de reescrita por seção [Lucas]

Definido no piloto da robot-docs#62 (Cap. 3, Interface entre o Controlador e o Sequenciador, 15/11/2026), que só
passou na terceira versão: as duas primeiras tinham as métricas limpas, mas erravam no conteúdo e em fatos. Por isso,
o processo vale mais que os critérios da seção seguinte.

Revisto pelo Lucas em 16/11/2026, na reescrita do Cap. 3: o mapa prévio e a passada de fato frase a frase atrasavam
sem melhorar o texto, e o erro recorrente era enxugar o texto antigo preservando todo fato, em frases densas.

1. **Redação direta, pela clareza, e não pela completude.** Escrever a partir da ideia, e não enxugando o texto antigo:
   primeiro o problema e o porquê, em palavras técnicas claras, uma coisa por frase. Número e detalhe só se o leitor os
   usa naquele ponto; o resto vai para o Teste, a Folha ou o repositório. Na dúvida, a versão mais curta.
2. **Registro** dos pedidos da orientadora, com as correções dela em roxo como gabarito de estilo.
3. **Autorrevisão de leitor:** cada termo apresentado antes do uso, cada frase decorre da anterior e nomeia de que fala
   ("que reação? que caminho?").
4. **Figuras e quadros** ficam só se mostram uma relação que o texto corrido não mostra.
5. **`medir_redacao.py` só como alarme.** Número limpo não aprova o texto; o critério é a leitura clara.

## Conteúdo do parágrafo [Lucas]

- **Clareza antes de completude.** O texto explica primeiro o papel de cada elemento: o que é, quem produz, quem usa
  e para quê, por extenso, e não inferido da tabela. A tabela traz o dado; o texto, o papel.
- **Dois níveis de abstração.** As seções anteriores aos Testes descrevem a implementação em nível alto, na medida do
  necessário para entender o mecanismo. O detalhe de implementação que um Teste usa entra na seção do Teste. O resto
  fica no repositório.
- **Uma ideia por parágrafo**, numa cadeia em que cada frase decorre da anterior. O conectivo só aparece onde a relação
  existe.
- **Cada afirmação é verdadeira no sentido exato.** O termo técnico afirma mais que a palavra comum e, por isso, exige
  conferência.
- **Sem premissa nova não demonstrada** e sem generalizar a partir de um caso.
- **Sem contraste com alternativa que o leitor não viu.**
- Repetir um assunto em mais de uma seção é normal no texto acadêmico; corta-se só quando a leitura melhora.

Exemplo (piloto, parágrafo do estado). Primeira versão, reprovada:

> A mensagem de estado (State) representa as condições ativas como estado, e não como eventos: cada código ocupa um bit
> de uma máscara de falhas ou de reflexos [...]. Compete ao sequenciador detectar o início e o término de cada
> condição [...].

O leitor não sabe de onde vem a mensagem nem para que serve; a máscara de bits e o contraste "estado, e não eventos"
são detalhe de código. Segunda versão, reprovada: três ideias num parágrafo, "a falha reaparece" (ela se repete),
"*best effort* descarta a mensagem" (só não a reenvia) e "cada mensagem substitui a anterior" generalizado para todos
os tópicos. Versão aprovada:

> O controlador publica o estado a cada ciclo de controle, de 10 ms, e cada publicação repete todas as falhas e
> reflexos ativos. Assim, se uma mensagem se perde no enlace, a publicação seguinte informa ao sequenciador as mesmas
> condições 10 ms depois. Como o comando e a odometria também são republicados periodicamente, nenhum tópico exige
> retransmissão, e todos utilizam a entrega sem confirmação do ROS 2 (*best effort*), na qual a mensagem perdida não é
> reenviada.

## Linguagem

- Argumentativa, impessoal, concisa, clara e objetiva, coerente e coesa [O] 42.
- Voz impessoal, 3ª pessoa do singular [P] 251. "Desenvolveu-se", "verificou-se", "optou-se"; nunca "desenvolvemos" [O] 57.
- O autor faz, e não o trabalho. "Apresenta-se neste trabalho o desenvolvimento", e não "este trabalho desenvolve" ou
  "este trabalho tem por objetivo" [C] 12.
- Os pronomes ele, ela, dele, dela, nele e nela são proibidos. Seu e sua saem do texto ou viram artigo [O] 56. Vale
  para os dois grupos, mesmo onde a orientadora usou o possessivo (decisão do Lucas, 15/11/2026, robot-docs#62 C).
- Tempos verbais: todos os verbos no presente ou no infinitivo, inclusive nos resultados (decisão do Lucas,
  16/11/2026). Substitui o [P] 251, que pede pretérito perfeito nos resultados e imperfeito nos comentários. O
  condicional fica só no que é hipotético ("exporia", "seria retirado").
- Registro culto: "demonstra", e não "mostra"; "afirma", e não "diz" [C] 4.
- Clareza é exatidão: sem palavra ambígua, rebuscada ou abstrata [O] 60. Exemplos a evitar: "condições extremas",
  "grande carga", "variações significativas", "novas tecnologias" [O] 61–62.
- Advérbio de quantidade ou qualidade (grande, pequeno, muito, pouco, bastante, mais, menos, maior, menor, melhor,
  pior) só em comparação explícita com outro item [O] 82.
- Adjetivos a evitar: sempre, nunca, rápido, lento, bom, ótimo, excelente, alto nível [O] 76.
- Redundâncias a evitar: "de grande importância", "mais eficiente", "completamente eficiente", "maior eficácia",
  "grande maioria", "conclui-se finalmente", "síntese final" [O] 75.
- Vícios a evitar [O] 74:
  - "através" fora do sentido de atravessar;
  - "gerar" no sentido de "resultar".
- Generalização exige citação [O] 63.

## Parágrafo e coesão

- Cada parágrafo tem um tópico frasal (a ideia central), defendido com argumento lógico e, de preferência, com
  dados [O] 24.
- Tamanho [O] 22, 24:
  - frases de até 40 palavras;
  - parágrafos de até 100 palavras, de 6 a 8 linhas, com duas frases. O limite é alarme, e não regra rígida: o critério
    é uma ideia por parágrafo, com teto de cerca de 130 palavras (robot-docs#62 B).
- No meio da frase, o conectivo vai entre vírgulas (", portanto,", ", contudo,") [O] 80. A orientadora abre parágrafos
  com "Além disso," e "Ademais," [Or].
- "Esse" retoma o que já foi dito; "este" indica o presente ou o que vem a seguir. Exemplos: "dessa forma",
  "este trabalho" [O] 73.
- Sem remissão vaga ao próprio texto ("supracitado", "acima", "abaixo", "anteriormente", "a seguir", "como já dito").
  Se for preciso, cite de novo [O] 84. A remissão explícita a capítulo, seção, figura, tabela ou apêndice é permitida
  ("apresentados no Capítulo 2") [Or]; [P] 187.
- Enumeração na própria frase, com dois-pontos e ponto e vírgula, é permitida: "três desses métodos: o ensaio,
  que...; a inspeção, que...; e a análise, que..." [Or].
- Aspas só em citação direta de até 3 linhas. O destaque vai em itálico ou negrito [O] 79; [P] 192.
- Sigla: na primeira ocorrência, o nome por extenso seguido da sigla entre parênteses; depois, só a sigla. Toda sigla
  entra na lista de siglas [O] 85; [P] 205.

## Citação

- O sobrenome entra direto: "Faghri (2014) afirma". Nada de "o estudo de", "segundo o autor", "ainda de acordo com o
  autor" [O] 83.
- Se as frases do parágrafo vêm do mesmo autor, cita-se uma vez, no fim do parágrafo [O] 33.
- "Segundo X (ano)," vale só para a 1ª frase: a 2ª frase precisa da própria citação [O] 35–36.
- Várias obras na mesma citação ficam em ordem alfabética, separadas por ponto e vírgula:
  "(Castro, 2023; Lopes, 2014; Tavares, 2024)" [O] 39–40.
- Página: é obrigatória na citação direta. Na indireta é opcional, e o livro sugere omitir para não confundir com a
  citação direta [P] 191, 195.
- Citação de citação usa "apud", só quando não houve acesso ao original [P] 189–190.
- Ideia de outra fonte se cita desde a Introdução [C] 28.
- Na Fundamentação Teórica:
  - todo parágrafo tem citação direta ou indireta [O] 32;
  - cada subtítulo tem ao menos 3 autores [O] 24.
- Em livro técnico, quando o autor reproduz a ideia de outro, cita-se o autor original [C] 50.

## Ilustrações, tabelas, quadros e equações

- Toda ilustração é citada no texto e inserida o mais perto possível do trecho que a chama [P] 206.
  - O título vai acima.
  - A fonte vai abaixo, obrigatória mesmo quando é autoria própria [P] 206.
  - A palavra "Figura" leva maiúscula na remissão do texto [O] 66.
- Não repetir num gráfico dados que já estão numa tabela [P] 207.
- Evitar ilustrações nos apêndices e anexos [P] 207.
- **Tabela:**
  - o dado central é numérico, em geral tratado estatisticamente [O] 69; [P] 208;
  - tem laterais abertas e `\hline` entre todas as linhas [Or] (os slides e o livro descrevem tabela sem linhas entre
    as linhas, [O] 69; [P] 210);
  - toda tabela tem unidade de medida no cabeçalho ou na coluna indicadora [P] 209;
  - se passar de uma página, cada página leva "continua", "continuação" ou "conclusão" e repete o cabeçalho [P] 210.
- **Quadro:** conteúdo textual, sem elaboração matemática ou estatística. Tem as laterais fechadas e todas as linhas
  internas [O] 70; [P] 214. Float textual é quadro, e o numérico segue como tabela (robot-docs#62 A). Texto com
  números embutidos (limites, parâmetros, resultados por requisito) é quadro: o número fica na frase, sem coluna com
  unidade no cabeçalho [P] 209.
- **Convenções de LaTeX** (robot-thesis 4fba562):
  - quadro com o ambiente `quadro` e colunas com `|`, como no `template.tex`; tabela com `\hline` e sem `|`;
  - rótulo `qua:` no quadro e `tab:` na tabela;
  - `\setlength{\extrarowheight}{1pt}` em todo float, logo após o `\label`: é o mínimo para o texto não encostar no
    filete;
  - caminho longo em `\texttt` leva `\allowbreak` depois da barra para não atravessar o filete;
  - float mais alto que o espaço abaixo da chamada usa `[htbp]`, e não `[H]`: com `[H]`, ele salta para a página
    seguinte e deixa o branco que [O] 72 proíbe. Os quadros saem em fila: um quadro que não cabe trava todos os
    quadros seguintes até o próximo `\FloatBarrier` ou `\clearpage` (robot-thesis 0a72bfb).
- **Equação:**
  - é chamada no texto antes de aparecer ("Equação 1"), e um "onde ..." define os símbolos depois [O] 67;
  - o número vai entre parênteses, à direita;
  - a quebra de linha fica antes do "=" ou depois de um operador [P] 206.
- Não pode sobrar espaço grande em branco no fim de uma página [O] 72.

## Estrutura

- O caráter monográfico pede foco no substancial: sem retomadas históricas longas nem contextualização ampla [P] 173.
- O título registra o objetivo geral ou os resultados e é coerente com ele. Exemplo: título "Projeto de...",
  objetivo "Projetar..." [C] 5, 21.
- Problema [P] 121; [C] 16:
  - em forma de pergunta;
  - claro e verificável;
  - relaciona duas ou mais variáveis.
- Hipótese: resposta provisória e testável ao problema [P] 122–123. Em estudo descritivo, pode ficar implícita no
  objetivo.
- Objetivos [P] 124; [C] 21, 26:
  - começam com verbo de ação;
  - os específicos são metas, e não tarefas;
  - os específicos seguem a ordem das fases da pesquisa.
- Classificação da pesquisa [P] 51–70; [C] 57:
  - natureza: básica ou aplicada;
  - objetivos: exploratória, descritiva ou explicativa;
  - procedimento: bibliográfica, experimental, estudo de caso, Design Science...;
  - abordagem: quantitativa, qualitativa ou mista;
  - instrumentos e método de análise.
- O Cap. 2 se chama "Fundamentação Teórica", como no template, e não "Revisão Bibliográfica" [C] 31. A
  Fundamentação responde só às questões da pesquisa [C] 30.
- Apêndice é elaborado pelo autor; anexo é documento de terceiros [C] 79.

## Roteiros por capítulo

Esqueleto para os capítulos ainda não escritos. Cada item é um parágrafo, ou um bloco de parágrafos.

**Resumo** [C] 8–12:
1. contextualização;
2. tema;
3. problema;
4. objetivo;
5. método;
6. resultado.

O Resumo tem um parágrafo só, de 180 a 250 palavras [C] 8 (faixa que também cabe na NBR 6028:2021, a confirmar na
norma; robot-docs#62 F), e começa sem "Este trabalho". As palavras-chave são de 3 a 5, em minúsculas e separadas
por ponto e vírgula [C] 9; [I] 54.

**Introdução** [C] 16–18, complementada por [P] 252:
1. contextualização da área, sem referência;
2. tema, com referência;
3. problema em forma de pergunta, com referência;
4. base teórica: autores clássicos e pesquisas dos últimos 5 a 10 anos, com referência;
5. justificativa com trabalhos similares e a diferença desta proposta, com referência;
6. objetivo geral, sem referência;
7. metodologia em resumo, com referência;
8. resultado geral, que responde à pergunta do item 3, sem referência.

O livro acrescenta a hipótese e um resumo das partes do trabalho. A Introdução é a última parte a ser escrita
[P] 252. Depois dela vêm os subitens Objetivo Geral e Objetivos Específicos [C] 15.

**Fundamentação Teórica** [C] 54:
- breve histórico da área;
- conceitos essenciais para o problema;
- estudos similares;
- explicação teórica do método;
- análise crítica que liga à Metodologia.

O leitor não pode chegar à Metodologia sem entender os conceitos que ela usa.

**Metodologia** [C] 54, 56:
- abre com a classificação da pesquisa;
- descreve o procedimento passo a passo, de forma que outro pesquisador possa replicá-lo;
- relata os equívocos e as decisões que se mostraram erradas.

A explicação teórica do método fica na Fundamentação.

**Resultados** [C] 73: precisão, imparcialidade e honestidade; um resultado para cada item da Metodologia.

**Discussão** [C] 74; [P] 253:
- analisa os resultados frente ao objetivo geral, aos específicos e às hipóteses;
- compara com as referências da Fundamentação.

**Conclusão** [C] 76; [P] 253–254:
1. "Tratou-se de [tema] ao abordar [problema], com o método [Y], para [objetivo]";
2. as constatações ("constatou-se", "verificou-se"), com a resposta à pergunta do problema e as hipóteses
   confirmadas e o porquê;
3. limitações e dificuldades que restringiram o alcance;
4. contribuições;
5. continuação da pesquisa (autocrítica).

## Uso de IA (orientação da disciplina)

A professora aceita IA para [C] 37; [I] 60, 64:
- revisar, corrigir a ortografia e dar coesão a texto escrito pelo autor;
- conferir informações e referências;
- receber prompts específicos.

Tudo passa por revisão crítica do autor.
