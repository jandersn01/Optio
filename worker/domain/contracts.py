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


class SearchRequestedEvent(BaseModel):
    """Evento publicado pela app quando o usuário cria uma busca."""
    type: str
    search_request_id: int
    user_id: int
    notification_email: str = Field(min_length=1)
    keywords: str = Field(min_length=1)
    area: str = ""
    modality: str = ""
    state: str = ""

    @classmethod
    def from_payload(cls, payload: dict) -> "SearchRequestedEvent":
        """Constrói e valida o evento, traduzindo qualquer erro em InvalidMessageError."""
        try:
            event = cls.model_validate(payload)
        except ValidationError as error:
            raise InvalidMessageError(f"Payload inválido: {error}") from error
        if event.type != "search_requested":
            raise InvalidMessageError(f"Tipo de mensagem desconhecido: {event.type}")
        return event

    @property
    def criteria(self) -> SearchCriteria:
        return SearchCriteria(
            keywords=self.keywords,
            area=self.area,
            modality=self.modality,
            state=self.state,
        )


# ── DTOs internos dos jobs de notificação ──

@dataclass
class Recipient:
    id: int
    email: str


@dataclass
class PreferenceGroup:
    criteria: SearchCriteria
    recipients: list[Recipient] = field(default_factory=list)


@dataclass
class AlertSpec:
    id: int
    name: str
    criteria: SearchCriteria


@dataclass
class UserAlerts:
    recipient: Recipient
    alerts: list[AlertSpec] = field(default_factory=list)


@dataclass
class DigestSection:
    alert_name: str
    courses: list[CourseData] = field(default_factory=list)
