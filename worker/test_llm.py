"""Testes para providers/llm.py — parse_llm_response e call_llm.

Task 1: Validação de relevância dos resultados
Task 4: Worker consome fila e chama API de LLM
"""
import json
import pytest
from unittest.mock import patch, MagicMock

from providers.llm import parse_llm_response, call_llm, VALID_MODALITIES, VALID_STATES


class TestParseLlmResponseDegradacao:
    """Testes de degradação: JSON malformado, courses ausente, curso sem name."""

    def test_json_malformado_retorna_lista_vazia(self):
        """JSON inválido não levanta exceção, retorna lista vazia."""
        resultado = parse_llm_response("isso não é JSON {{{")
        assert resultado == []

    def test_resposta_vazia_retorna_lista_vazia(self):
        """String vazia ou None não levanta exceção."""
        assert parse_llm_response("") == []
        assert parse_llm_response("   ") == []

    def test_courses_ausente_retorna_lista_vazia(self):
        """JSON válido sem campo 'courses' retorna lista vazia."""
        resposta = json.dumps({"other_field": "value"})
        resultado = parse_llm_response(resposta)
        assert resultado == []

    def test_curso_sem_name_e_descartado(self):
        """Curso sem 'name' é ignorado, outros são mantidos."""
        resposta = json.dumps({
            "courses": [
                {"name": "", "institution": "UFPB"},  # name vazio
                {"institution": "UFCG"},  # sem name
                {"name": "Engenharia de Software", "institution": "IFPB"},  # válido
            ]
        })
        resultado = parse_llm_response(resposta)
        assert len(resultado) == 1
        assert resultado[0]["name"] == "Engenharia de Software"

    def test_curso_com_name_apenas_espacos_e_descartado(self):
        """Curso com name contendo apenas espaços é ignorado."""
        resposta = json.dumps({
            "courses": [
                {"name": "   ", "institution": "UFPB"},
                {"name": "Ciência de Dados", "institution": "UFCG"},
            ]
        })
        resultado = parse_llm_response(resposta)
        assert len(resultado) == 1
        assert resultado[0]["name"] == "Ciência de Dados"


class TestParseLlmResponseNormalizacao:
    """Testes de normalização e validação de modality/state contra enums."""

    def test_modality_valida_normalizada_para_lowercase(self):
        """Modalidade válida em uppercase é normalizada para lowercase."""
        resposta = json.dumps({
            "courses": [
                {"name": "Curso A", "modality": "EAD"},
                {"name": "Curso B", "modality": "PRESENCIAL"},
                {"name": "Curso C", "modality": "Hibrido"},
            ]
        })
        resultado = parse_llm_response(resposta)
        assert resultado[0]["modality"] == "ead"
        assert resultado[1]["modality"] == "presencial"
        assert resultado[2]["modality"] == "hibrido"

    def test_modality_invalida_vira_string_vazia(self):
        """Modalidade fora do domínio vira string vazia."""
        resposta = json.dumps({
            "courses": [
                {"name": "Curso A", "modality": "semi-presencial"},
                {"name": "Curso B", "modality": "online"},
                {"name": "Curso C", "modality": ""},
            ]
        })
        resultado = parse_llm_response(resposta)
        assert resultado[0]["modality"] == ""
        assert resultado[1]["modality"] == ""
        assert resultado[2]["modality"] == ""

    def test_state_valido_normalizado_para_uppercase(self):
        """Estado válido em lowercase é normalizado para uppercase."""
        resposta = json.dumps({
            "courses": [
                {"name": "Curso A", "state": "pb"},
                {"name": "Curso B", "state": "sp"},
                {"name": "Curso C", "state": "RJ"},
            ]
        })
        resultado = parse_llm_response(resposta)
        assert resultado[0]["state"] == "PB"
        assert resultado[1]["state"] == "SP"
        assert resultado[2]["state"] == "RJ"

    def test_state_invalido_vira_string_vazia(self):
        """Estado fora do domínio vira string vazia."""
        resposta = json.dumps({
            "courses": [
                {"name": "Curso A", "state": "XX"},
                {"name": "Curso B", "state": "Brasil"},
                {"name": "Curso C", "state": ""},
            ]
        })
        resultado = parse_llm_response(resposta)
        assert resultado[0]["state"] == ""
        assert resultado[1]["state"] == ""
        assert resultado[2]["state"] == ""

    def test_valores_validos_sao_mantidos(self):
        """Valores válidos de modality e state são preservados."""
        resposta = json.dumps({
            "courses": [
                {
                    "name": "Mestrado em IA",
                    "institution": "UFPB",
                    "modality": "ead",
                    "state": "PB",
                    "link": "https://ufpb.br/curso"
                }
            ]
        })
        resultado = parse_llm_response(resposta)
        assert len(resultado) == 1
        curso = resultado[0]
        assert curso["name"] == "Mestrado em IA"
        assert curso["institution"] == "UFPB"
        assert curso["modality"] == "ead"
        assert curso["state"] == "PB"
        assert curso["link"] == "https://ufpb.br/curso"

    def test_valid_modalities_contem_valores_esperados(self):
        """VALID_MODALITIES contém ead, presencial, hibrido."""
        assert "ead" in VALID_MODALITIES
        assert "presencial" in VALID_MODALITIES
        assert "hibrido" in VALID_MODALITIES

    def test_valid_states_contem_estados_brasileiros(self):
        """VALID_STATES contém siglas de estados brasileiros."""
        assert "PB" in VALID_STATES
        assert "SP" in VALID_STATES
        assert "RJ" in VALID_STATES
        assert len(VALID_STATES) == 27  # 26 estados + DF


class TestCallLlmComExcecao:
    """Testes de call_llm com o client OpenAI mockado lançando exceção.

    Task 4: Comportamento esperado — a exceção é PROPAGADA (não capturada),
    pois o SearchProcessor é responsável por tratar e publicar FAILED.
    """

    @patch("providers.llm._get_client")
    def test_excecao_de_api_e_propagada(self, mock_get_client):
        """Exceção da API OpenAI é propagada para o chamador."""
        from openai import APIError

        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = APIError(
            message="API Error",
            request=MagicMock(),
            body=None
        )
        mock_get_client.return_value = mock_client

        with pytest.raises(APIError):
            call_llm("prompt de teste")

    @patch("providers.llm._get_client")
    def test_timeout_e_propagado(self, mock_get_client):
        """Timeout da API é propagado para o chamador."""
        from openai import APITimeoutError

        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = APITimeoutError(
            request=MagicMock()
        )
        mock_get_client.return_value = mock_client

        with pytest.raises(APITimeoutError):
            call_llm("prompt de teste")

    @patch("providers.llm._get_client")
    def test_resposta_valida_retorna_content(self, mock_get_client):
        """Resposta válida retorna o content da mensagem."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '{"courses": []}'
        mock_response.usage = MagicMock(total_tokens=100)
        mock_client.chat.completions.create.return_value = mock_response
        mock_get_client.return_value = mock_client

        resultado = call_llm("prompt de teste")
        assert resultado == '{"courses": []}'

    @patch("providers.llm._get_client")
    def test_content_none_retorna_string_vazia(self, mock_get_client):
        """Se content for None, retorna string vazia."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = None
        mock_response.usage = None
        mock_client.chat.completions.create.return_value = mock_response
        mock_get_client.return_value = mock_client

        resultado = call_llm("prompt de teste")
        assert resultado == ""
