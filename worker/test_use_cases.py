"""Testes para domain/use_cases.py — SearchProcessor.

Task 4: Worker consome fila e chama API de LLM
"""
import pytest
from unittest.mock import MagicMock, call

from domain.use_cases import SearchProcessor
from domain.contracts import JobRequest, SearchCriteria, CourseData


class TestSearchProcessorProcess:
    """SearchProcessor.process() fluxo completo."""

    def _make_request(self, job_id="123", job_type="manual", email="user@test.com"):
        """Helper para criar um JobRequest de teste."""
        return JobRequest(
            job_id=job_id,
            job_type=job_type,
            notification_email=email,
            criteria=SearchCriteria(
                keywords="engenharia",
                area="engenharias",
                modality="ead",
                state="PB"
            )
        )

    def _make_courses(self):
        """Helper para criar lista de CourseData de teste."""
        return [
            CourseData(
                name="Mestrado em Engenharia",
                institution="UFPB",
                modality="ead",
                state="PB",
                link="https://ufpb.br/curso"
            ),
            CourseData(
                name="Doutorado em IA",
                institution="UFCG",
                modality="presencial",
                state="PB",
                link="https://ufcg.br/curso"
            )
        ]

    def test_finder_retorna_cursos_publica_completed(self):
        """Finder retorna cursos → publica status=COMPLETED com os cursos."""
        mock_publisher = MagicMock()
        mock_finder = MagicMock()
        courses = self._make_courses()
        mock_finder.find.return_value = courses

        processor = SearchProcessor(publisher=mock_publisher, finder=mock_finder)
        request = self._make_request()

        processor.process(request)

        # Verifica que finder foi chamado com os critérios corretos
        mock_finder.find.assert_called_once_with(request.criteria)

        # Verifica que publisher foi chamado com status COMPLETED e cursos
        mock_publisher.publish_result.assert_called_once()
        call_kwargs = mock_publisher.publish_result.call_args.kwargs
        assert call_kwargs["job_id"] == "123"
        assert call_kwargs["job_type"] == "manual"
        assert call_kwargs["status"] == "COMPLETED"
        assert call_kwargs["email"] == "user@test.com"
        assert call_kwargs["courses"] == courses
        assert call_kwargs["criteria"] == request.criteria.model_dump()

    def test_finder_retorna_lista_vazia_publica_no_results(self):
        """Finder retorna lista vazia → publica status=NO_RESULTS."""
        mock_publisher = MagicMock()
        mock_finder = MagicMock()
        mock_finder.find.return_value = []

        processor = SearchProcessor(publisher=mock_publisher, finder=mock_finder)
        request = self._make_request()

        processor.process(request)

        mock_publisher.publish_result.assert_called_once()
        call_kwargs = mock_publisher.publish_result.call_args.kwargs
        assert call_kwargs["status"] == "NO_RESULTS"
        assert call_kwargs["courses"] == []

    def test_finder_lanca_excecao_publica_failed_sem_propagar(self):
        """Finder lança exceção → publica status=FAILED, não propaga a exceção."""
        mock_publisher = MagicMock()
        mock_finder = MagicMock()
        mock_finder.find.side_effect = Exception("Erro no Firecrawl")

        processor = SearchProcessor(publisher=mock_publisher, finder=mock_finder)
        request = self._make_request()

        # Não deve levantar exceção — o worker não pode cair
        processor.process(request)

        mock_publisher.publish_result.assert_called_once()
        call_kwargs = mock_publisher.publish_result.call_args.kwargs
        assert call_kwargs["status"] == "FAILED"
        assert call_kwargs["job_id"] == "123"
        # Quando há exceção, courses NÃO é passado (confirmado no código)
        assert "courses" not in call_kwargs

    def test_finder_retorna_none_trata_como_no_results(self):
        """Se finder retornar None (edge case), trata como lista vazia."""
        mock_publisher = MagicMock()
        mock_finder = MagicMock()
        mock_finder.find.return_value = None

        processor = SearchProcessor(publisher=mock_publisher, finder=mock_finder)
        request = self._make_request()

        processor.process(request)

        call_kwargs = mock_publisher.publish_result.call_args.kwargs
        # None é falsy, então status deve ser NO_RESULTS
        assert call_kwargs["status"] == "NO_RESULTS"

    def test_dados_do_request_sao_passados_corretamente(self):
        """Verifica que todos os dados do request são passados ao publisher."""
        mock_publisher = MagicMock()
        mock_finder = MagicMock()
        mock_finder.find.return_value = self._make_courses()

        processor = SearchProcessor(publisher=mock_publisher, finder=mock_finder)
        request = self._make_request(
            job_id="456",
            job_type="alert_requested",
            email="outro@test.com"
        )

        processor.process(request)

        call_kwargs = mock_publisher.publish_result.call_args.kwargs
        assert call_kwargs["job_id"] == "456"
        assert call_kwargs["job_type"] == "alert_requested"
        assert call_kwargs["email"] == "outro@test.com"
