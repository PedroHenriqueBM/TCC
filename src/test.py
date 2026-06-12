"""
Demonstração do fluxo completo do sistema de qualidade de software com IA.

Antes de executar:
  1. Copie .env.example para .env e preencha as variáveis
  2. Execute: export OPENAI_API_KEY='sua-chave'
  3. Execute: export GOOGLE_CLIENT_ID='seu-client-id'
  4. Execute: export GOOGLE_CLIENT_SECRET='seu-client-secret'

Execute a partir da raiz do projeto:
  cd src && python test.py
"""

from Database.database import initialize_database

# Inicializa o banco de dados (cria tabelas se não existirem)
initialize_database()

# ─────────────────────────────────────────────
# 0. LOGIN COM GOOGLE
# ─────────────────────────────────────────────
# from Model.Auth.Services.GoogleAuthService.google_auth_service import login_with_google, get_current_user
# user = login_with_google()  # Abre o navegador para autenticação
# print(f"Usuário autenticado: {user}")

# ─────────────────────────────────────────────
# 1. CRIAR PROJETO (com validação por agente de conformidade)
# ─────────────────────────────────────────────
# from Model.Projects.Services.CreateProjectService.create_project import create_project
# projeto = create_project(
#     name="Sistema de Busca Web",
#     description="Plataforma que permite ao usuário pesquisar informações na internet de forma rápida."
# )
# print(f"Projeto criado: {projeto.get_id()} — {projeto.get_name()}")

# ─────────────────────────────────────────────
# 2. CRIAR PERSONA (com validação por agente de conformidade)
# ─────────────────────────────────────────────
# from Model.Projects.Services.CreatePersonaService.create_persona import create_persona
# persona = create_persona(
#     project_id=projeto.get_id(),
#     name="Ana Desenvolvedora",
#     opportunities="O sistema pode ajudar Ana a encontrar documentação técnica rapidamente.",
#     key_attributes="Desenvolvedora sênior, 28 anos, alta fluência tecnológica.",
#     description="Profissional de TI que usa mecanismos de busca diariamente para pesquisa técnica.",
#     needs="Busca rápida e resultados precisos para termos técnicos.",
#     challenges="Resultados pouco relevantes para termos específicos de programação."
# )
# print(f"Persona criada: {persona.get_id()} — {persona.get_name()}")

# ─────────────────────────────────────────────
# 3. CRIAR REQUISITO FUNCIONAL (formato ARO, validado por agente)
# ─────────────────────────────────────────────
# from Model.Projects.Services.CreateFunctionalRequirementService.create_functional_requirement import create_functional_requirement
# requisito = create_functional_requirement(
#     project_id=projeto.get_id(),
#     name="O usuário pesquisa informações na internet utilizando o campo de busca",
#     url="https://www.google.com/",
#     persona_ids=[persona.get_id()]
# )
# print(f"Requisito criado: {requisito.get_id()} — {requisito.get_name()}")

# ─────────────────────────────────────────────
# 4. CRIAR CRITÉRIO DE ACEITE (formato Gherkin, validado por agente)
# ─────────────────────────────────────────────
# from Model.Projects.Services.CreateAcceptanceCriteriaService.create_acceptance_criteria import create_acceptance_criteria
# criterio = create_acceptance_criteria(
#     requirement_id=requisito.get_id(),
#     content=(
#         "Given que o usuário está na página inicial do Google\n"
#         "When o usuário digita um termo no campo de busca e pressiona Enter\n"
#         "Then o sistema exibe uma lista de resultados relevantes para o termo pesquisado"
#     ),
#     author="Tester"
# )
# print(f"Critério de aceite criado: {criterio['id']}")

# ─────────────────────────────────────────────
# 5. GRAVAR EXECUÇÃO DA FUNCIONALIDADE
# ─────────────────────────────────────────────
# from Model.UsabilityInspection.Services.CreateFunctionalityVideoRecordService.create_functionality_video_record import create_functionality_video_record
# path = create_functionality_video_record(requisito.get_id())
# print(f"Gravação salva em: {path}")

# ─────────────────────────────────────────────
# FLUXO COM DADOS JÁ EXISTENTES (ID "001")
# ─────────────────────────────────────────────

# Para testar com o requisito "001" já gravado, insira-o no banco primeiro:
from Database.repositories.functional_requirement_repository import functional_requirement_exists, create_functional_requirement
from Database.repositories.acceptance_criteria_repository import create_acceptance_criteria

if not functional_requirement_exists("001"):
    create_functional_requirement(
        id="001",
        project_id="demo",
        name="O usuário pesquisa informações na internet utilizando o campo de busca do Google",
        url="https://www.google.com/"
    )
    create_acceptance_criteria(
        id="ac-001",
        requirement_id="001",
        content=(
            "Given que o usuário está na página inicial do Google\n"
            "When o usuário digita um termo no campo de busca e pressiona Enter\n"
            "Then o sistema exibe uma lista de resultados relevantes"
        ),
        author="Tester"
    )
    print("Requisito '001' inserido no banco de dados.")

# ─────────────────────────────────────────────
# 7. INSPEÇÃO DE USABILIDADE
# ─────────────────────────────────────────────
from Model.UsabilityInspection.Services.ExecuteUsabilityInspectionService.execute_usability_inspection import execute_usability_inspection

print("\n=== EXECUTANDO INSPEÇÃO DE USABILIDADE ===")
resultado_inspecao = execute_usability_inspection(
    functionality_id="001",
    tester_comment=""  # Opcional: comentário do tester para refinar a análise
)
print("\nResultado da inspeção:")
print(resultado_inspecao)

# ─────────────────────────────────────────────
# 8. TESTE DE SISTEMA
# ─────────────────────────────────────────────
# from Model.SystemTest.Services.ExecuteSystemTestService.execute_system_test import execute_system_test

# print("\n=== EXECUTANDO TESTE DE SISTEMA ===")
# execucao = execute_system_test(
#     requirement_id="001",
#     tester_comment=""  # Opcional: comentário do tester
# )
# print(f"\nTeste de Sistema — Passou: {execucao.get_passed()}")
