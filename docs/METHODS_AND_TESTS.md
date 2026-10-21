# Métodos, testes e critérios

## Etapas
1. Entrevistas com moradores, associação, operador, técnico e gestor para mapear o fluxo vigente.
2. Definição de requisitos, papéis, responsabilidades, estados e privacidade.
3. Desenvolvimento do fluxo de ocorrência ponta a ponta.
4. Testar regras locais antes de integrar IA generativa.
5. Avaliar triagem com revisão humana e fallback local.
6. Testar telemetria simulada e só depois projetar bancada física.
7. Piloto em campo apenas com autorização e parceiro confirmado.

## Cenários automáticos
- Operação normal
- Perda de alimentação
- Alimentação presente e corrente zero
- Vibração fora do limite demonstrativo
- Ausência de leituras/comunicação

## Critérios iniciais
- Testes determinísticos das regras aprovados.
- Nunca encaminhar para responsável não confirmado.
- Cada mudança de estado fica no histórico.
- Resolução exige nota sobre providência/verificação.
- Metas simuladas de latência (10 s para falha persistente, 60 s para perda de comunicação) ainda não validadas por ensaio.
- Indicadores de campo continuam “a medir”.

## Métricas
Tempo de registro até encaminhamento, aceite, primeira atualização e reparo; proporção com responsável confirmado; reabertura; encaminhamento incorreto; qualidade da classificação; satisfação; disponibilidade.
