---
data: 2026-10-23
status: provisório
camada: "interface controlador–sequenciador"
revoga:
revogada_por:
affects: []
evidence: [V-04]
---
# 026 – TF odom → base_link publicado no RPi pelo pacote odom_to_tf_ros2

## Problema

O SLAM obtém a pose pelo TF. O TF é assinado com QoS reliable, e um assinante reliable não recebe de um publicador best effort, que é a QoS de todo o enlace (ADR 025).

## Decisão

O pacote `odom_to_tf_ros2`, rodando no RPi, assina a odometria publicada pelo controlador e transmite o TF odom → base_link. Ele usa o carimbo de tempo original da odometria (ADR 027) e não guarda estado.

## Alternativa descartada

- **ESP32 publicando o TF:** exigiria uma exceção reliable no enlace, com retransmissões e espera de confirmação na tarefa micro-ROS, e faria a pose trafegar duas vezes.
- **Nó próprio:** reimplementaria uma função que um pacote mantido já oferece.
- **Filtro de estimação (EKF):** não há outra fonte para fundir hoje.

## Racional

- O enlace fica uniforme em best effort. A conversão de QoS é feita onde não custa nada ao enlace nem ao ESP32.
- Usar um pacote pronto e configurável evita código a justificar. Ele é infraestrutura de interface, sem lógica de camada.
- O carimbo é configurável (original ou hora atual), o que permite recuar da ADR 027 sem mudar código.

## Nota

- Verificar se a assinatura do pacote é compatível com best effort. Se não for, ajustar por configuração ou trocar por um nó próprio equivalente.
- Uma IMU (BNO085 disponível) tornaria o EKF a alternativa natural. Fica como issue no `robot-docs`, fora do escopo atual.
