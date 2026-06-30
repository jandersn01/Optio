import json
import logging
import os

from openai import OpenAI

from providers.prompts import SYSTEM_PROMPT
from domain.choices import SearchModality,SearchStates_Br

logger = logging.getLogger("optio.worker.llm")

LLM_MODEL = os.getenv("LLM_MODEL", "openai/gpt-4o-mini")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

_client: OpenAI | None = None

# Derivado dos enums canônicos (fonte única em search.choices).
VALID_MODALITIES = {m.value for m in SearchModality}
VALID_STATES = {s.value for s in SearchStates_Br}


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(
            api_key=os.getenv("OPENROUTER_API_KEY"),
            base_url=OPENROUTER_BASE_URL,
        )
    return _client


def call_llm(prompt: str) -> str:
    client = _get_client()
    logger.info("Chamando LLM. model=%s", LLM_MODEL)

    response = client.chat.completions.create(
        model=LLM_MODEL,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
        max_tokens=4096,
    )

    result = response.choices[0].message.content

    usage = getattr(response, "usage", None)
    total_tokens = getattr(usage, "total_tokens", None)
    logger.info("LLM respondeu. tokens_used=%s", total_tokens)

    return result or ""


def parse_llm_response(response_text: str) -> list[dict]:
    if not response_text or not response_text.strip():
        logger.warning("Resposta vazia do LLM; tratando como sem resultados.")
        return []

    try:
        data = json.loads(response_text)
    except json.JSONDecodeError:
        logger.warning("Resposta do LLM não é JSON válido; tratando como sem resultados.")
        return []

    raw_courses = data.get("courses", [])

    courses = []
    for item in raw_courses:
        name = item.get("name", "").strip()
        if not name:
            continue

        modality = item.get("modality", "").lower().strip()
        state = item.get("state", "").upper().strip()

        courses.append({
            "name": name,
            "institution": item.get("institution", "").strip(),
            "modality": modality if modality in VALID_MODALITIES else "",
            "state": state if state in VALID_STATES else "",
            "link": item.get("link", "").strip(),
        })

    logger.info("Cursos extraídos do LLM. count=%d", len(courses))
    return courses