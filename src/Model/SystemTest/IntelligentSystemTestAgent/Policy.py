class SystemTestPolicy:

    def get_system_prompt(self) -> str:
        return (
            "Você é um agente inteligente de Teste de Sistema de software. "
            "Sua função principal é avaliar visualmente gravações de funcionalidades "
            "(fornecidas como PDF) e determinar se os critérios de aceite foram atendidos. "
            "Quando solicitado, você também reescreve scripts Playwright para corrigir falhas "
            "causadas por mudanças na interface.\n\n"
            "Ao reescrever um script, siga estas regras:\n"
            "1. Mantenha a estrutura assíncrona com async/await e async_playwright;\n"
            "2. Preserve os imports necessários;\n"
            "3. Use seletores mais robustos (text, role, label) em vez de seletores CSS frágeis;\n"
            "4. Adicione waits apropriados (wait_for_selector, wait_for_load_state);\n"
            "5. O script deve ser executável standalone via 'asyncio.run(main())';\n"
            "6. Use headless=True para execução automatizada;\n"
            "7. Retorne APENAS o código Python, sem explicações ou blocos markdown."
        )

    def get_rewrite_prompt(self, script: str, error: str, acceptance_criteria: str) -> str:
        return (
            f"O seguinte script de teste Playwright falhou com o erro:\n"
            f"```\n{error}\n```\n\n"
            f"Critérios de Aceite que o teste deve verificar:\n"
            f"{acceptance_criteria}\n\n"
            f"Script atual:\n"
            f"```python\n{script}\n```\n\n"
            f"Reescreva o script para corrigir o problema. "
            f"Retorne APENAS o código Python corrigido, sem explicações."
        )

    def get_pdf_evaluation_prompt(self, requirement_name: str, acceptance_criteria: str,
                                   script_summary: str, previous_comments: str) -> str:
        return (
            f"Requisito Funcional: {requirement_name}\n\n"
            f"Critérios de Aceite:\n{acceptance_criteria}\n\n"
            f"Script executado (contexto do que foi feito, NÃO é o critério de avaliação):\n"
            f"{script_summary[:1500] if script_summary else '(não disponível)'}\n\n"
            f"Avaliações anteriores:\n{previous_comments or '(nenhuma)'}\n\n"
            "O PDF anexado contém a gravação da execução da funcionalidade, "
            "convertida em frames (páginas do PDF).\n\n"
            "Analise VISUALMENTE o PDF e determine se cada critério de aceite foi cumprido "
            "com base no que aparece nas telas gravadas.\n\n"
            "Retorne EXCLUSIVAMENTE um JSON válido (sem markdown, sem texto extra) neste formato:\n"
            '{"passed": true_ou_false, "evaluation": "avaliação em português, máx 8 linhas, '
            'indicando quais critérios foram atendidos ou violados e por quê"}'
        )

    def get_evaluation_prompt(self, requirement_name: str, acceptance_criteria: str,
                               returncode_passed: bool, stdout: str, stderr: str,
                               previous_comments: str) -> str:
        status = "PASSOU (código de saída 0)" if returncode_passed else "FALHOU (código de saída não-zero ou timeout)"
        return (
            f"O script de teste para o Requisito Funcional '{requirement_name}' {status}.\n\n"
            f"Critérios de Aceite:\n{acceptance_criteria}\n\n"
            f"Saída (stdout):\n{stdout or '(vazia)'}\n\n"
            f"Erros (stderr):\n{stderr or '(nenhum)'}\n\n"
            f"Comentários de execuções anteriores:\n{previous_comments or '(nenhum)'}\n\n"
            f"Analise se a execução realmente verificou e atendeu os critérios de aceite acima.\n\n"
            f"REGRAS PARA 'passed':\n"
            f"- Se o script falhou (código de saída não-zero, exceção ou timeout): 'passed' = false.\n"
            f"- Se o script não contém verificações explícitas dos critérios (expect, assert, check):\n"
            f"  'passed' = false — navegar com sucesso não equivale a validar os critérios.\n"
            f"- Somente marque 'passed' = true se há evidência clara na saída de que cada\n"
            f"  critério de aceite foi exercitado e verificado com sucesso.\n\n"
            f"Retorne EXCLUSIVAMENTE um JSON válido com este formato (sem markdown, sem texto extra):\n"
            f'{{"passed": true_ou_false, "evaluation": "avaliação em português, máximo 5 linhas"}}'
        )
