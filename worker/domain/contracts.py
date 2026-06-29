"""Contratos de dados tipados que trafegam entre as camadas e entre app↔worker.

Centraliza o "contrato" antes espalhado em dicts soltos (`payload.get(...)`):
- `SearchRequestedEvent`: mensagem recebida da fila (validada via pydantic).
- `SearchCriteria`: critérios de busca (keywords + filtros), usados pelo finder.
- `CourseData`: curso retornado pela pipeline.
Os demais são DTOs internos dos jobs de notificação.
"""
from dataclasses import dataclass, field

from pydantic import BaseModel, Field, ValidationError

from domain.exceptions import InvalidMessageError


class SearchCriteria(BaseModel):
    keywords: str = ""
    area: str = ""
    modality: str = ""
    state: str = ""


class CourseData(BaseModel):
    name: str
    institution: str = ""
    modality: str = ""
    state: str = ""
    link: str = ""

class JobRequest(BaseModel):
    """Novo formato universal de pedido que vem da fila"""

    job_id: str        # Pode ser o ID do SearchRequest ou do Alerta
    job_type: str      # 'manual', 'alert' ou 'preference'
    notification_email: str = ""
    criteria: SearchCriteria

    @classmethod
    def from_payload(cls, payload: dict) -> "JobRequest":
        try:
            return cls.model_validate(payload)
        except Exception as error:
            raise InvalidMessageError(f"Payload inválido: {error}")