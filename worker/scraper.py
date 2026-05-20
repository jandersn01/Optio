import os
import logging

from firecrawl import FirecrawlApp

logger = logging.getLogger("optio.worker.scraper")

FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY", "")
MAX_PAGES = 10


def _build_query(payload: dict) -> str:
    parts = ["pós-graduação", payload.get("keywords", ""), "gratuito", "universidade federal estadual instituto federal"]
    if area := payload.get("area"):
        parts.append(area)
    modality = payload.get("modality", "")
    if modality and modality != "all":
        parts.append(modality)
    if state := payload.get("state"):
        parts.append(state)
    return " ".join(filter(None, parts))


def search_courses_web(payload: dict) -> str:
    query = _build_query(payload)
    logger.info("Iniciando busca web. query=%r", query)

    app = FirecrawlApp(api_key=FIRECRAWL_API_KEY)
    response = app.search(query, limit=MAX_PAGES)

    # Firecrawl v2: response é SearchData diretamente, com atributo .web
    web_results = getattr(response, "web", None) or []

    logger.info("Firecrawl retornou %d resultados web.", len(web_results))

    entries = []
    for item in web_results:
        if isinstance(item, dict):
            url = item.get("url", "")
            title = item.get("title", "")
            description = item.get("description", "")
        else:
            url = getattr(item, "url", "")
            title = getattr(item, "title", "")
            description = getattr(item, "description", "")

        if title or description:
            entries.append(f"Título: {title}\nDescrição: {description}\nLink: {url}")

    raw_text = "\n\n---\n\n".join(entries)
    logger.info("Busca web concluída. entries=%d chars=%d", len(entries), len(raw_text))
    return raw_text
