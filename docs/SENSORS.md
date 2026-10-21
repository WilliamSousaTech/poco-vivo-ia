# Sensores e bancada futura

Não comprar sensores industriais antes de confirmar tipo de bomba, tensão, corrente nominal, diâmetro da tubulação, vazão e condições ambientais.

| Sinal | Opção de bancada | Posicionamento futuro | Limite |
|---|---|---|---|
| Estado esperado | Variável de software/comando | Entrada lógica do controlador, quando acessível e autorizada | Necessário distinguir parada normal |
| Corrente DC | ACS712 compatível com bomba de baixa tensão ou medidor DC apropriado | Bancada, no circuito DC conforme datasheet | Não utilizar módulo didático em rede de motor AC |
| Presença de alimentação | Relé monitor de tensão com saída isolada | Quadro elétrico por profissional habilitado | Escolher para sistema monofásico/trifásico correto |
| Corrente AC | Transformador SCT-013 compatível | Ao redor de um único condutor individual | Circuito de condicionamento/sinal obrigatório |
| Vazão | YF-S201 para circuito pequeno compatível | Em linha, após a bomba, com orientação de fluxo correta | Não é universal para poço real |
| Nível | HC-SR04 só em bancada seca/protegida; JSN-SR04T conforme limites | Acima da superfície d'água, protegido de intempéries | Confirmar zona morta e faixa de medição |
| Vibração | MPU-6050/ADXL345 como experimento | Fixação rígida no motor, se acessível | Experimental, não substitui sensor industrial |

## Segurança
O protótipo de software não comanda motores. Não conecte GPIO do ESP32 à rede elétrica. Medição de rede exige isolamento, condicionamento, proteção e instalação por profissional qualificado, observando NR-10 e orientações do fabricante. Sensores de corrente/vazão/nível não determinam potabilidade.
