# Log de Projeto: Arquitetura da PMU (Power Entry & Safety System)

**Data:** 31/01/2026 | **Gate:** G3 | **Stage:** S7 (Design PDB)

### 1. Objetivo do Stage
Projetar o esquemático da Unidade de Gerenciamento de Energia (PMU), garantindo proteção contra transientes de motores, inversão de polaridade e implementação de um sistema de parada de emergência (E-Stop) fail-safe.

### 2. Especificações do Setup
- **Tensão Nominal:** 11.1V (Bateria LiPo 3S)
- **Proteção de Entrada:** Fusível automotivo 15A + TVS Unidirecional SM6T15A.
- **Drivers de Motor:** 2x DRV8871 (Corrente de pico 3.6A cada).
- **MCU de Segurança:** ESP32 (Monitoramento de barramento e controle de E-Stop).

### 3. Decisões e Resultados Técnicos
- **Hierarquia de Grounding:** Implementação de Star Grounding separando `GND_BAT` (motores) de `GND` (lógica) através de um *Net Tie*.
- **Topologia de Segurança (E-Stop):** - Chaveamento High-Side via MOSFET Canal P (IRF4905).
    - Acionamento isolado via optoacoplador PC817.
    - Botão físico NF (Normalmente Fechado) inserido no loop de corrente do optoacoplador para garantir segurança positiva (fail-safe).
- **Feedback de Barramento:**
    - Monitoramento redundante: Telemetria quantitativa via INA226 (I2C) e feedback binário isolado via segundo optoacoplador.
    - Lógica invertida no feedback (Energia presente = LOW no ESP32) para detecção automática de ruptura de cabos.
- **Filtragem de EMI:** - Adição de capacitores cerâmicos de 100nF na entrada dos optoacopladores (pós-botão de emergência) para mitigar ruído induzido por cabos longos.

### 4. Próximos Passos
- Finalizar a folha `REGULATION_5V` com os 2 UBECs isolados.
- Dimensionar larguras de trilhas de potência para suportar $I_{peak}$ de 10A com elevação térmica de < 10°C.