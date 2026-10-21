# Poço Vivo — MVP v0.1 💧

**Da comunidade para quem resolve — com transparência até a água voltar.**

Plataforma web demonstrativa para registrar ocorrências de abastecimento comunitário, sugerir uma triagem, encaminhar ao responsável cadastrado, acompanhar providências e registrar a confirmação de recuperação.

> **Estado:** protótipo de software com dados sintéticos. Ainda não está ligado a poços reais, não envia solicitações a órgãos públicos e não comprova impacto em campo.

## O que esta versão contém

- Interface web responsiva para registar e acompanhar ocorrências.
- API Python/FastAPI e documentação automática.
- Banco SQLite local com comunidades de demonstração.
- Motor local de triagem por regras, sem custo por chamada.
- Integração opcional com um modelo da OpenAI para sugerir categoria/perguntas, com saída validada e fallback local.
- Encaminhamento somente quando há responsável marcado como confirmado no cadastro.
- Histórico de eventos para mudanças de status.
- Simulador de operação normal, perda de alimentação, motor sem corrente, funcionamento irregular e ausência de comunicação.
- Testes automatizados e pipeline de testes do GitHub Actions.
- Documentação de arquitetura, métodos, testes, sensores e roadmap.

## Instalação — Windows PowerShell

Requisitos: Python 3.11 ou superior (recomendado Python 3.12).

```powershell
git clone https://github.com/WilliamSousaTech/poco-vivo-ia.git
cd poco-vivo-ia
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload
```

Acesse:
- Plataforma: http://127.0.0.1:8000
- Documentação da API: http://127.0.0.1:8000/docs
- Verificação de saúde: http://127.0.0.1:8000/api/health

Se o PowerShell bloquear a ativação do ambiente virtual, use:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

## Instalação — Linux / WSL

```bash
git clone https://github.com/WilliamSousaTech/poco-vivo-ia.git
cd poco-vivo-ia
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

## Testes

```bash
pytest -q
```

## Como demonstrar

1. Inicie o servidor.
2. Registre uma ocorrência pelo botão **Registrar ocorrência**.
3. Escolha uma das comunidades fictícias. A comunidade São José tem um responsável demonstrativo confirmado; Boa Vista não tem responsável cadastrado e deve ficar em triagem.
4. Abra a ocorrência e atualize o status, registrando notas de atendimento.
5. Na visão geral, clique nos cenários em **Laboratório de simulação**.
6. Consulte os resultados na página **Telemetria simulada**.

Os nomes e dados das comunidades são fictícios. Não use esta interface para abrir chamados reais.

## IA opcional

Sem chave, o protótipo utiliza regras locais. Para testar uma IA generativa, preencha `.env`:

```dotenv
OPENAI_API_KEY=sua_chave
OPENAI_MODEL=modelo_disponivel_na_sua_conta
```

Reinicie o servidor. Não faça commit do arquivo `.env`; ele está no `.gitignore`. O custo e a disponibilidade dependem da conta/provedor. A IA sugere categoria e perguntas; não escolhe um responsável fora do cadastro, não confirma diagnóstico e não encerra ocorrências.

Evite enviar dados pessoais sensíveis para a API externa. A chave nunca deve ficar no frontend.

## Estrutura

```text
app/
  main.py                 # API e endpoints
  database.py             # SQLite e dados demonstrativos
  schemas.py              # validação Pydantic
  services/
    triage.py             # regras e IA opcional
    rules_engine.py       # cenários e regras de telemetria
  static/
    index.html            # interface
    styles.css            # identidade visual responsiva
    app.js                # interações do painel
tests/
  test_logic.py
docs/
  ARCHITECTURE.md
  SENSORS.md
  METHODS_AND_TESTS.md
  ROADMAP.md
  REFERENCES.md
.github/workflows/tests.yml
```

## Próximos marcos

1. Validar o processo real com moradores, operadores, técnicos e gestores.
2. Rever o cadastro de responsáveis e regras de encaminhamento com uma organização parceira.
3. Implementar autenticação, perfis de acesso, proteção de dados e notificações reais antes de qualquer piloto.
4. Construir uma bancada de baixa tensão com ESP32 e sensores.
5. Calibrar medições e validar cenários antes de estudar um poço real.

## Segurança e limites

- Não há autenticação de produção nem controle robusto de permissões.
- Não existe integração com Água e Vida, GISÁGUA, Fiscaliza Fácil ou outros sistemas.
- O encaminhamento exibido é interno e demonstrativo; nenhum destinatário real é notificado.
- As regras de telemetria têm limiares ilustrativos, não um diagnóstico industrial.
- O software não controla bombas, motores ou relés.
- **Nunca conecte pinos do ESP32 diretamente à rede elétrica do motor.** Medição elétrica real exige isolamento, componentes adequados, projeto de proteção e profissional qualificado, observando normas aplicáveis como a NR-10.

## Fontes técnicas

Veja [docs/REFERENCES.md](docs/REFERENCES.md).