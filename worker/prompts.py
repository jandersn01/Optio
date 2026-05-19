SYSTEM_PROMPT = """Você é um assistente especializado em educação superior brasileira.
Sua tarefa é analisar conteúdo de páginas web e extrair informações sobre cursos de pós-graduação.

Regras obrigatórias:
- Retorne APENAS JSON válido, sem texto adicional antes ou depois
- Para o campo "modality", use exatamente um destes valores: "ead", "presencial", "hibrido" — ou "" se desconhecido
- Para o campo "state", use exatamente a sigla de 2 letras (ex: "SP", "PB", "RJ") — ou "" se desconhecido
- Inclua apenas cursos claramente identificados no conteúdo fornecido
- Não invente informações ausentes no conteúdo
"""


def build_prompt(payload: dict, raw_content: str) -> str:
    filter_lines = []
    if keywords := payload.get("keywords"):
        filter_lines.append(f"- Palavras-chave: {keywords}")
    if area := payload.get("area"):
        filter_lines.append(f"- Área: {area}")
    modality = payload.get("modality", "")
    if modality and modality != "all":
        filter_lines.append(f"- Modalidade preferida: {modality}")
    if state := payload.get("state"):
        filter_lines.append(f"- Estado preferido: {state}")

    filters_text = "\n".join(filter_lines) if filter_lines else "Nenhum filtro específico."

    return f"""Analise o conteúdo abaixo e extraia todos os cursos de pós-graduação encontrados.

Filtros da busca:
{filters_text}

Conteúdo das páginas:
{raw_content}

Retorne um JSON no seguinte formato:
{{
  "courses": [
    {{
      "name": "Nome completo do curso",
      "institution": "Nome da instituição",
      "modality": "ead|presencial|hibrido ou vazio",
      "state": "Sigla UF ou vazio",
      "link": "URL do curso ou vazio"
    }}
  ]
}}

Se nenhum curso for encontrado, retorne {{"courses": []}}."""