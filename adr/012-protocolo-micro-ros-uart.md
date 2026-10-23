---
data: 2026-10-10
status: provisório
camada: "Controlador / Sequenciador"
revoga:
revogada_por:
affects: []
evidence: []
---
# 012 - Protocolo entre controlador e computador embarcado

## Problema

Definir o protocolo de comunicação entre o microcontrolador (controlador) e o computador embarcado (sequenciador/deliberador) sobre o enlace serial UART.

## Decisão

Usar micro-ROS (XRCE-DDS) com transporte serial UART e agente micro-ROS no RPi 5. O controlador expõe tópicos ROS 2: recebe seleção de comportamento e parâmetros (cmd_vel + modo) e publica odometria e estado/falha.

## Alternativa descartada

Protocolo próprio sobre UART (enquadramento COBS/SLIP + CRC) com nó-ponte no ROS 2.

## Racional

Menos elementos a projetar e verificar: enquadramento, CRC e ponte já prontos; fonte única das mensagens no robot-interfaces; o controlador aparece no grafo ROS, o que permite verificar a interface com ferramentas padrão (ros2 topic hz, rosbag). A banda necessária é baixa, já que o LiDAR vai ao RPi por USB.
