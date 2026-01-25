# AMR Project - Logbook
Diário do desenvolvimento do projeto, contendo informações pertinentes a testes, código e montagem do protótipo.

## Estrutura de pastas
A estrutura de pastas deve ser orientada à metodologia Agile Stage-Gate do projeto. Deve-se criar pastas de Gates com pastas de Stages contendo anotações:

```text
amr-docs/
├── README.md               # O "Índice Mestre" (Table of Contents)
├── G1_Digital_Twin/
│   ├── S1_URDF/
│   │   ├── 2026-01-25_log_config_frames.md
│   │   └── 2026-01-26_teste_colisao_gazebo.md
│   └── S2_SLAM_Sim/
├── G2_HIL_Performance/
│   └── S3_MicroROS_Bridge/
│       └── 2026-02-05_analise_latencia_serial.md
└── ... (G3, G4, G5, G6, G7, ...)
```

## Como documentar tarefas do protótipo?
Utilizar arquivo de template de log quando for realizar qualquer tarefa relacionada ao projeto.

> [!IMPORTANT]
> Quando parar a tarefa no meio para continuar depois, realizar anotações do que foi feito e realizar um commit. Depois, quando continuar a tarefa, retomar o log e finalizá-lo.

As pastas do repositório são organizadas em relação ao assunto do log e conforme necessidade.

## Log Template
>  # {YYYY-MM-DD_titulo-curto.md}
> Data: dd/mm/yyyy hh:mm
>
> Autor:
>
> Finalizada? (Sim/Não):
>
> Repositório e commits relacionados (obrigatório):
>
> ---
>
> Descrição da(s) tarefa(s):
>
> Justificativa (Por que escolher este método/componente/estrutura e não outro(a)?):
>
> Performance e métricas esperadas (O que se espera conseguir com esta tarefa? Citar fonte de performance e métricas esperadas):
>
> Performance e métricas resultantes (O que se obteve com esta tarefa? Incluir imagens, prints, vídeos, gifs):
>
> Literatura relacionada (citar pelo menos 1 fonte, pode ser site):
>
> Testes realizados (realizar pelo menos 1 teste):
>
> Testes relacionados:
>
> Dúvidas e sugestões de tarefas futuras (obrigatório):
> 
