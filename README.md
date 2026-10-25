# robot-docs

Documentação viva do TCC: plataforma robótica móvel com arquitetura em três camadas (Gat, 1998),
com o controlador num ESP32-S3 e o sequenciador e o deliberador num RPi 5 (ROS 2).

## Mapa

| Caminho | Responde |
| :---: | :---: |
| `arquitetura.md` | Como o sistema é hoje (cita as ADRs, não as repete) |
| `adr/` | Por que ele é assim |
| `requisitos.md`, `objetivos.md` | O que o sistema precisa cumprir |
| `verifications/` | Como se prova que cumpre |
| `notas/` | O que aconteceu na bancada (anotações cruas) |
| `evidencias/` | Registros dos ensaios (bags), citados nas verificações e nas notas |
| `hardware/` | Cabeamento e ligações |
| `referencias/` | Material de apoio |
| Issues do GitHub | O que está em aberto agora (labels `medicao`, `decisao`, `adr`; a issue fixada é o próximo passo) |

## Fluxo de cada passo

1. Decidir só o que o passo exige. Decisão que iria para a monografia vira ADR (`provisório`).
2. Claude Code propõe o plano; você aprova.
3. Diffs pequenos, lidos antes de rodar.
4. Checagem de bancada do passo.
5. Anotação crua em `notas/`. A ADR vira `definitivo` quando a evidência existe.

Commits citam a ADR ou a verificação correspondente, quando houver, e fecham a issue com `Closes #N`.
