"""Testes para domain/contracts.py — JobRequest.from_payload.

Task 4: Worker consome fila e chama API de LLM
Garante que payloads malformados levantam InvalidMessageError.
"""
import pytest

from domain.contracts import JobRequest, SearchCriteria
from domain.exceptions import InvalidMessageError


class TestJobRequestFromPayload:
    """JobRequest.from_payload() com payload malformado."""

    def _valid_payload(self):
        """Payload válido para referência."""
        return {
            "job_id": "123",
            "job_type": "manual",
            "notification_email": "user@test.com",
            "criteria": {
                "keywords": "engenharia",
                "area": "engenharias",
                "modality": "ead",
                "state": "PB"
            }
        }

    def test_payload_valido_retorna_job_request(self):
        """Payload válido retorna JobRequest corretamente."""
        payload = self._valid_payload()
        request = JobRequest.from_payload(payload)

        assert request.job_id == "123"
        assert request.job_type == "manual"
        assert request.notification_email == "user@test.com"
        assert request.criteria.keywords == "engenharia"
        assert request.criteria.area == "engenharias"
        assert request.criteria.modality == "ead"
        assert request.criteria.state == "PB"

    def test_sem_job_id_levanta_invalid_message_error(self):
        """Payload sem job_id levanta InvalidMessageError."""
        payload = self._valid_payload()
        del payload["job_id"]

        with pytest.raises(InvalidMessageError):
            JobRequest.from_payload(payload)

    def test_sem_job_type_levanta_invalid_message_error(self):
        """Payload sem job_type levanta InvalidMessageError."""
        payload = self._valid_payload()
        del payload["job_type"]

        with pytest.raises(InvalidMessageError):
            JobRequest.from_payload(payload)

    def test_sem_criteria_levanta_invalid_message_error(self):
        """Payload sem criteria levanta InvalidMessageError."""
        payload = self._valid_payload()
        del payload["criteria"]

        with pytest.raises(InvalidMessageError):
            JobRequest.from_payload(payload)

    def test_criteria_com_tipo_errado_levanta_invalid_message_error(self):
        """Criteria como string em vez de dict levanta InvalidMessageError."""
        payload = self._valid_payload()
        payload["criteria"] = "isso deveria ser um dict"

        with pytest.raises(InvalidMessageError):
            JobRequest.from_payload(payload)

    def test_criteria_como_lista_levanta_invalid_message_error(self):
        """Criteria como lista em vez de dict levanta InvalidMessageError."""
        payload = self._valid_payload()
        payload["criteria"] = ["keywords", "area"]

        with pytest.raises(InvalidMessageError):
            JobRequest.from_payload(payload)

    def test_criteria_como_none_levanta_invalid_message_error(self):
        """Criteria como None levanta InvalidMessageError."""
        payload = self._valid_payload()
        payload["criteria"] = None

        with pytest.raises(InvalidMessageError):
            JobRequest.from_payload(payload)

    def test_job_id_como_numero_e_aceito(self):
        """job_id como número é aceito (Pydantic converte para string)."""
        payload = self._valid_payload()
        payload["job_id"] = 123  # número em vez de string

        # Pydantic deve converter para string ou aceitar
        request = JobRequest.from_payload(payload)
        # O resultado pode ser string "123" ou int 123 dependendo da config
        assert str(request.job_id) == "123"

    def test_notification_email_vazio_e_aceito(self):
        """notification_email vazio é aceito (campo tem default)."""
        payload = self._valid_payload()
        payload["notification_email"] = ""

        request = JobRequest.from_payload(payload)
        assert request.notification_email == ""

    def test_sem_notification_email_usa_default_vazio(self):
        """Sem notification_email usa o default (string vazia)."""
        payload = self._valid_payload()
        del payload["notification_email"]

        request = JobRequest.from_payload(payload)
        assert request.notification_email == ""

    def test_criteria_com_campos_extras_e_aceito(self):
        """Criteria com campos extras é aceito (Pydantic ignora extras)."""
        payload = self._valid_payload()
        payload["criteria"]["campo_extra"] = "ignorado"

        request = JobRequest.from_payload(payload)
        assert request.criteria.keywords == "engenharia"

    def test_criteria_com_campos_vazios_e_aceito(self):
        """Criteria com todos os campos vazios é aceito."""
        payload = {
            "job_id": "123",
            "job_type": "manual",
            "criteria": {
                "keywords": "",
                "area": "",
                "modality": "",
                "state": ""
            }
        }

        request = JobRequest.from_payload(payload)
        assert request.criteria.keywords == ""
        assert request.criteria.area == ""

    def test_payload_completamente_vazio_levanta_invalid_message_error(self):
        """Payload vazio ({}) levanta InvalidMessageError."""
        with pytest.raises(InvalidMessageError):
            JobRequest.from_payload({})

    def test_payload_none_levanta_invalid_message_error(self):
        """Payload None levanta InvalidMessageError ou TypeError."""
        with pytest.raises((InvalidMessageError, TypeError)):
            JobRequest.from_payload(None)
