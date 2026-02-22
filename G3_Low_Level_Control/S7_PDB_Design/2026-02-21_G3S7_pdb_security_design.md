# Log de Tarefa: Refinamento de Segurança e Grounding da PDB

- **Data:** 21/02/2026
- **Autor:** Lucas Francisco Vieira
- **Gate/Stage:** G3.S7 (Motion Control / PDB Design)
- **Tarefa Relacionada:** Implementação de isolamento e lógica de E-Stop

## 1. Implementação Técnica (KiCad)
Nesta sessão, foram aplicadas as mudanças na arquitetura de potência para garantir conformidade com a ADR 023 e 024.

### Malha de Terra e Alimentação
- **Star Grounding:** Criado o nó NetTie para unir `GND_LOGIC` e `GND_BAT` apenas no terminal da bateria.
- **Ilhas de 5V:** Segmentação concluída entre `+5V_SBC` (UBEC 1) e `+5V_LOGIC` (UBEC 2).

### Circuito de Segurança (E-Stop)
Foi implementada a lógica de comando em cascata para vencer a indutância dos 60cm de cabeamento externo:
1. **Estágio Buffer:** Transistor NPN (BC847) com $R_B = 1k\Omega$.
2. **Estágio Isolador:** Optoacoplador PC817 alimentado pelos 5V filtrados, garantindo $I_F \approx 16,3mA$.
3. **Estágio de Potência:** Preparado para MOSFET P-Channel em lógica de corte por pull-up (Fail-safe).

## 2. Verificação de Cálculos
- **Leitura 12V (Divisor):** Garantida tensão de $3.26V$ para o GPIO do ESP32.
- **Filtro de Ruído:** Capacitor de $100nF$ em paralelo ao LED do opto para supressão de EMI dos motores.

## 3. Observações de Execução
`reflect:` A decisão de usar o driver transistorizado antes do optoacoplador elimina a preocupação com a queda de tensão nos 60cm de fio e protege o GPIO de curtos acidentais no chassi, validando o pilar de robustez do projeto.