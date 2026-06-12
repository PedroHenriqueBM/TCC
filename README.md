# QA Automatizado com IA

Ferramenta de automação de qualidade de software desenvolvida como TCC do curso de Engenharia de Software. Combina **inspeção de usabilidade** e **teste de sistema** por meio de agentes de inteligência artificial generativa.

## Visão geral

O sistema automatiza duas atividades centrais de qualidade:

- **Inspeção de Usabilidade** — um agente analisa gravações em vídeo da funcionalidade usando as 10 heurísticas de Nielsen e uma base de conhecimento interna.
- **Teste de Sistema** — um agente executa scripts Playwright gerados durante a gravação, detecta falhas, reescreve o script quando a interface muda e avalia o resultado.

Todos os artefatos (projetos, personas, requisitos, critérios de aceite, execuções, comentários) são persistidos em SQLite.

## Arquitetura

O projeto segue **Domain-Driven Design (DDD)** com três domínios:

```
TCC/
├── run_web.py                      # Entry point da aplicação web
├── requirements.txt
├── .env.example
└── src/
    ├── web/                        # Camada de apresentação — Flask + Bootstrap 5
    │   ├── __init__.py             # Flask app factory
    │   ├── routes.py               # Todas as rotas HTTP
    │   └── templates/              # Templates Jinja2
    │       ├── base.html           # Layout base com sidebar
    │       ├── index.html          # Dashboard
    │       ├── projetos.html
    │       ├── personas.html
    │       ├── requisitos.html
    │       ├── inspecao.html
    │       └── teste.html
    ├── Database/
    │   ├── database.py             # SQLite — inicialização e conexão
    │   └── repositories/           # Repositórios por entidade
    ├── AppSettings.py              # Persistência de configurações (JSON + env vars)
    ├── Model/
    │   ├── Auth/                   # Domínio genérico — Google OAuth
    │   ├── Projects/               # Domínio de suporte — Projetos, Personas, Requisitos
    │   │   ├── ConformityAgents/   # Agentes de conformidade (OpenAI GPT-4o)
    │   │   └── Services/
    │   ├── UsabilityInspection/    # Domínio core — Inspeção com IA multimodal
    │   │   ├── IntelligentUsabilityInspectionAgent/
    │   │   └── Services/
    │   └── SystemTest/             # Domínio core — Teste automatizado com IA
    │       ├── IntelligentSystemTestAgent/
    │       └── Services/
    ├── Storage/
    │   ├── tcc.db                  # Banco SQLite
    │   └── <requirement_id>/       # Gravações, PDFs e scripts por requisito
    └── test.py                     # Script de seed / demonstração
```

### Tecnologias

| Tecnologia | Uso |
|---|---|
| Python 3.10 | Linguagem principal |
| Flask 3 | Interface web (BSD-3-Clause) |
| Bootstrap 5 | Estilização via CDN (MIT) |
| OpenAI API | Agentes de inspeção, teste e conformidade |
| Playwright | Gravação e execução de scripts de teste |
| SQLite | Persistência local |
| python-dotenv | Carregamento de variáveis de ambiente |

### Formatos obrigatórios

- **ARO** — Ator + Requisito + Objeto para requisitos funcionais  
  Exemplo: *"O usuário pesquisa informações na internet utilizando o campo de busca"*
- **Gherkin** — Given / When / Then para critérios de aceite
- **Heurísticas de Nielsen** — base da inspeção de usabilidade

### Governança de IA

Todos os agentes seguem o framework **AI-TMM (AI Trust Maturity Model)** com políticas de:
- Transparência e explicabilidade
- Justiça e mitigação de viés
- Segurança e robustez
- Privacidade e proteção de dados

## Instalação

### Pré-requisitos

- Python 3.10+
- Navegador Chromium (para Playwright)

### Passos

```bash
# 1. Clone o repositório
git clone <url-do-repositorio>
cd TCC

# 2. Crie e ative o ambiente virtual
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
# .venv\Scripts\activate    # Windows

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Instale os navegadores do Playwright
playwright install chromium

# 5. Configure as variáveis de ambiente
cp .env.example .env
# Edite .env com suas chaves
```

### Variáveis de ambiente (`.env`)

```env
# Chave da API OpenAI — https://platform.openai.com/api-keys
# Alternativa: configure pela interface em Configurações (sem precisar reiniciar)
OPENAI_API_KEY=sk-proj-...

# Opcional — chave secreta do Flask (gerada automaticamente se omitida)
# FLASK_SECRET_KEY=chave-aleatoria-segura
```

> A chave da OpenAI também pode ser configurada e atualizada pela interface web em **Configurações**, sem necessidade de reiniciar o servidor ou editar arquivos.

## Execução

```bash
# A partir da raiz do projeto
python run_web.py
```

Acesse **http://localhost:5000** no navegador.

> **Importante:** o app deve ser executado a partir da raiz do projeto (`TCC/`), não de dentro de `src/`, pois os caminhos de Storage são relativos ao CWD.

## Fluxo de uso

| Passo | Ação | Página |
|------:|------|--------|
| 1 | Criar projeto | **Projetos** |
| 2 | Criar personas | **Personas** |
| 3 | Criar requisito funcional (ARO) e critérios de aceite (Gherkin) | **Requisitos** |
| 4 | Gravar a execução da funcionalidade no navegador | **Inspeção** |
| 5 | Executar inspeção de usabilidade com IA | **Inspeção** |
| 6 | Executar teste de sistema automatizado com IA | **Teste de Sistema** |

## Páginas da interface

### Dashboard (`/`)
- Status do ambiente (API configurada)
- Métricas: projetos, requisitos, inspeções e testes executados
- Lista de projetos com seleção rápida
- Guia de uso

### Projetos (`/projetos`)
- Criar, editar e excluir projetos com validação por agente de conformidade
- Selecionar projeto ativo (persiste na sidebar via sessão Flask)
- Exclusão em cascata: remove personas, requisitos e todo o histórico

### Personas (`/personas`)
- Criar, editar e excluir personas com 6 campos validados por agente
- Listar personas do projeto ativo

### Requisitos (`/requisitos`)
- Criar, editar e excluir requisitos funcionais no formato ARO com validação
- Associar/reatribuir personas ao requisito
- Criar, editar e excluir critérios de aceite no formato Gherkin com validação
- Selecionar requisito ativo
- Exclusão em cascata: remove critérios, inspeções, testes e comentários

### Inspeção de Usabilidade (`/inspecao`)
- **Passo 1:** gravar execução — usa `playwright codegen` para capturar todas as interações (cliques, preenchimentos, navegações) em um script Python preciso; depois reproduz o script headless com gravação de vídeo para gerar o PDF
- **Passo 2:** executar inspeção — agente analisa o PDF com heurísticas de Nielsen
- Comentário do tester (opcional)
- Histórico de inspeções e comentários
- **Download** do PDF de gravação e do resultado de cada inspeção (`.txt`)

### Teste de Sistema (`/teste`)
- Visualizar o script Playwright gerado na gravação
- Executar teste: roda o script headless com gravação de vídeo para ter evidência da execução
- **Avaliação visual por PDF**: o agente analisa o PDF da gravação + critérios de aceite usando GPT-4o multimodal (mesmo mecanismo da inspeção). O script é apenas contexto do que foi feito — a IA olha as telas
- **Gravação de vídeo** da execução salva em `src/Storage/<req_id>/test_video_<exec_id>.webm`
- Comentário do tester (opcional)
- Histórico com badge passou/falhou, avaliação do agente e player de vídeo inline
- **Download** do script (`.py`), resultado (`.txt`) e vídeo da execução (`.webm`)
- **Seletor inline**: quando nenhum requisito está ativo, exibe formulário de seleção sem sair da página

### Configurações (`/configuracoes`)
- Configurar e atualizar a chave da API OpenAI pela interface (sem reiniciar o servidor)
- Exibe chave mascarada quando configurada; permite remover
- **Prompts personalizáveis** para cada um dos 5 agentes de conformidade — edite o system prompt diretamente na interface e restaure ao padrão com um clique
- Auto-seleção: se houver apenas 1 projeto ou 1 requisito, é selecionado automaticamente ao navegar

## Dependências

```
flask
openai
playwright
httpx
python-dotenv
```

## Banco de dados

| Tabela | Descrição |
|---|---|
| `users` | Usuários autenticados via Google |
| `projects` | Projetos cadastrados |
| `personas` | Personas por projeto |
| `functional_requirements` | Requisitos funcionais (ARO) |
| `requirement_personas` | Relação N:N requisito ↔ persona |
| `acceptance_criteria` | Critérios de aceite (Gherkin) |
| `usability_inspection_executions` | Registro de cada inspeção |
| `system_test_executions` | Registro de cada execução de teste |
| `comments` | Comentários de agentes e testers |

## Autor

Pedro Barros — Trabalho de Conclusão de Curso, Engenharia de Software
