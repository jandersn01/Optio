"""Testes para search/views.py — search_request_create.

Tasks 5 e 6: POST válido com modality e state cria SearchRequest
com esses valores salvos E o criteria publicado na fila contém
exatamente esses valores.
"""
from unittest.mock import patch, MagicMock

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from search.models import SearchRequest
from search.choices import SearchStatus

User = get_user_model()


class SearchRequestCreateViewTests(TestCase):
    """Testes da view search_request_create."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email="user@test.com",
            password="SenhaForte123!"
        )
        self.client.login(email="user@test.com", password="SenhaForte123!")
        self.url = reverse("search:request_create")

    def _form_data(self, keywords="engenharia de software", area="",
                   modality="", state=""):
        """Helper para criar dados do formulário."""
        return {
            "keywords": keywords,
            "area": area,
            "modality": modality,
            "state": state,
        }

    @patch("search.views.publish_search_request")
    def test_post_valido_cria_search_request(self, mock_publish):
        """POST válido cria SearchRequest no banco."""
        data = self._form_data(keywords="ciência de dados")

        response = self.client.post(self.url, data)

        self.assertEqual(SearchRequest.objects.count(), 1)
        search = SearchRequest.objects.first()
        self.assertEqual(search.keywords, "ciência de dados")
        self.assertEqual(search.user, self.user)
        self.assertEqual(search.status, SearchStatus.PENDING)

    @patch("search.views.publish_search_request")
    def test_post_com_modality_salva_no_banco(self, mock_publish):
        """POST com modality salva o valor no SearchRequest."""
        data = self._form_data(modality="ead")

        self.client.post(self.url, data)

        search = SearchRequest.objects.first()
        self.assertEqual(search.modality, "ead")

    @patch("search.views.publish_search_request")
    def test_post_com_state_salva_no_banco(self, mock_publish):
        """POST com state salva o valor no SearchRequest."""
        data = self._form_data(state="PB")

        self.client.post(self.url, data)

        search = SearchRequest.objects.first()
        self.assertEqual(search.state, "PB")

    @patch("search.views.publish_search_request")
    def test_post_com_modality_e_state_salva_ambos(self, mock_publish):
        """POST com modality e state salva ambos os valores."""
        data = self._form_data(modality="presencial", state="SP")

        self.client.post(self.url, data)

        search = SearchRequest.objects.first()
        self.assertEqual(search.modality, "presencial")
        self.assertEqual(search.state, "SP")

    @patch("search.views.publish_search_request")
    def test_publish_search_request_e_chamado(self, mock_publish):
        """publish_search_request é chamado após criar o SearchRequest."""
        data = self._form_data()

        self.client.post(self.url, data)

        mock_publish.assert_called_once()

    @patch("search.views.publish_search_request")
    def test_criteria_publicado_contem_modality_e_state(self, mock_publish):
        """O SearchRequest passado para publish contém os filtros corretos."""
        data = self._form_data(
            keywords="inteligência artificial",
            modality="hibrido",
            state="RJ"
        )

        self.client.post(self.url, data)

        # Verifica o argumento passado para publish_search_request
        mock_publish.assert_called_once()
        search_request = mock_publish.call_args[0][0]

        self.assertEqual(search_request.keywords, "inteligência artificial")
        self.assertEqual(search_request.modality, "hibrido")
        self.assertEqual(search_request.state, "RJ")

    @patch("search.views.publish_search_request")
    def test_criteria_publicado_com_area(self, mock_publish):
        """O SearchRequest passado para publish contém a área."""
        data = self._form_data(
            keywords="mestrado",
            area="engenharias",
            modality="ead",
            state="PB"
        )

        self.client.post(self.url, data)

        search_request = mock_publish.call_args[0][0]
        self.assertEqual(search_request.area, "engenharias")

    @patch("search.views.publish_search_request")
    def test_post_valido_redireciona_para_lista(self, mock_publish):
        """POST válido redireciona para a lista de buscas."""
        data = self._form_data()

        response = self.client.post(self.url, data)

        self.assertRedirects(response, reverse("search:request_list"))

    @patch("search.views.publish_search_request")
    def test_notification_email_e_preenchido(self, mock_publish):
        """notification_email é preenchido com o email do usuário."""
        data = self._form_data()

        self.client.post(self.url, data)

        search = SearchRequest.objects.first()
        self.assertEqual(search.notification_email, "user@test.com")

    def test_get_exibe_formulario(self):
        """GET exibe o formulário de busca."""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "search/search_request_form.html")

    def test_nao_autenticado_redireciona_para_login(self):
        """Usuário não autenticado é redirecionado para login."""
        self.client.logout()

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)


class SearchRequestCreateQueueErrorTests(TestCase):
    """Testes de erro na publicação na fila."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email="user@test.com",
            password="SenhaForte123!"
        )
        self.client.login(email="user@test.com", password="SenhaForte123!")
        self.url = reverse("search:request_create")

    @patch("search.views.publish_search_request")
    def test_erro_na_fila_marca_como_failed(self, mock_publish):
        """Erro na publicação marca o SearchRequest como FAILED."""
        from search.publisher import QueuePublishError
        mock_publish.side_effect = QueuePublishError("Erro na fila")

        data = {
            "keywords": "engenharia",
            "area": "",
            "modality": "",
            "state": "",
        }

        self.client.post(self.url, data)

        search = SearchRequest.objects.first()
        self.assertEqual(search.status, SearchStatus.FAILED)

    @patch("search.views.publish_search_request")
    def test_erro_na_fila_redireciona_para_formulario(self, mock_publish):
        """Erro na publicação redireciona de volta para o formulário."""
        from search.publisher import QueuePublishError
        mock_publish.side_effect = QueuePublishError("Erro na fila")

        data = {
            "keywords": "engenharia",
            "area": "",
            "modality": "",
            "state": "",
        }

        response = self.client.post(self.url, data)

        self.assertRedirects(response, reverse("search:request_create"))
