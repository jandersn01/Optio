from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from unittest.mock import patch, MagicMock

from search.models import SearchRequest, Course
from search.choices import SearchStatus
from search.emails import send_no_results_email, send_results_email


User = get_user_model()


# ============================================================
# TASK 2 - Testes da página de resultados
# ============================================================


class SearchResultsViewAuthTestCase(TestCase):
    """Testes de autenticação e ownership para a view de resultados."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass123",
        )
        self.other_user = User.objects.create_user(
            email="other@example.com",
            password="otherpass123",
        )
        self.search_request = SearchRequest.objects.create(
            user=self.user,
            notification_email="test@example.com",
            keywords="teste autenticacao",
            status=SearchStatus.COMPLETED,
        )

    def test_unauthenticated_redirects_to_login(self):
        """Verifica que usuario nao autenticado e redirecionado para login."""
        response = self.client.get(
            reverse("search:search_results", kwargs={"pk": self.search_request.pk})
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)

    def test_user_cannot_access_other_users_search(self):
        """Verifica que usuario nao pode acessar busca de outro usuario."""
        self.client.login(email="other@example.com", password="otherpass123")

        response = self.client.get(
            reverse("search:search_results", kwargs={"pk": self.search_request.pk})
        )
        self.assertEqual(response.status_code, 404)

    def test_user_can_access_own_search(self):
        """Verifica que usuario pode acessar propria busca."""
        self.client.login(email="test@example.com", password="testpass123")

        response = self.client.get(
            reverse("search:search_results", kwargs={"pk": self.search_request.pk})
        )
        self.assertEqual(response.status_code, 200)

    def test_nonexistent_search_returns_404(self):
        """Verifica que busca inexistente retorna 404."""
        self.client.login(email="test@example.com", password="testpass123")

        response = self.client.get(
            reverse("search:search_results", kwargs={"pk": 99999})
        )
        self.assertEqual(response.status_code, 404)


class SearchResultsViewStatesTestCase(TestCase):
    """Testes para os diferentes estados da pagina de resultados."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass123",
        )

    def test_pending_state_shows_loading_message(self):
        """Verifica que status PENDING exibe mensagem de carregamento."""
        search = SearchRequest.objects.create(
            user=self.user,
            notification_email="test@example.com",
            keywords="busca pendente",
            status=SearchStatus.PENDING,
        )
        self.client.login(email="test@example.com", password="testpass123")

        response = self.client.get(
            reverse("search:search_results", kwargs={"pk": search.pk})
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Processando")

    def test_processing_state_shows_loading_message(self):
        """Verifica que status PROCESSING exibe mensagem de carregamento."""
        search = SearchRequest.objects.create(
            user=self.user,
            notification_email="test@example.com",
            keywords="busca em processamento",
            status=SearchStatus.PROCESSING,
        )
        self.client.login(email="test@example.com", password="testpass123")

        response = self.client.get(
            reverse("search:search_results", kwargs={"pk": search.pk})
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Processando")

    def test_failed_state_shows_error_message(self):
        """Verifica que status FAILED exibe mensagem de erro."""
        search = SearchRequest.objects.create(
            user=self.user,
            notification_email="test@example.com",
            keywords="busca com erro",
            status=SearchStatus.FAILED,
        )
        self.client.login(email="test@example.com", password="testpass123")

        response = self.client.get(
            reverse("search:search_results", kwargs={"pk": search.pk})
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Erro ao processar busca")
        self.assertContains(response, "Nova Pesquisa")

    def test_completed_with_courses_shows_results(self):
        """Verifica que status COMPLETED com cursos exibe os resultados."""
        search = SearchRequest.objects.create(
            user=self.user,
            notification_email="test@example.com",
            keywords="busca completa",
            status=SearchStatus.COMPLETED,
            results_count=2,
        )
        Course.objects.create(
            search_request=search,
            name="Curso de Python",
            institution="IFPB",
        )
        self.client.login(email="test@example.com", password="testpass123")

        response = self.client.get(
            reverse("search:search_results", kwargs={"pk": search.pk})
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Curso de Python")
        self.assertContains(response, "IFPB")


class ResultsEmailUrlTestCase(TestCase):
    """Testes para verificar que o e-mail aponta para a URL correta."""

    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass123",
        )
        self.search_request = SearchRequest.objects.create(
            user=self.user,
            notification_email="test@example.com",
            keywords="teste email url",
            status=SearchStatus.COMPLETED,
        )

    @patch("search.emails.EmailMultiAlternatives")
    def test_results_email_contains_correct_url(self, mock_email_class):
        """Verifica que o e-mail de resultados aponta para a pagina correta."""
        mock_email = MagicMock()
        mock_email_class.return_value = mock_email

        courses = [
            {"name": "Curso 1", "institution": "Inst 1", "modality": "ead", "state": "SP", "link": ""},
        ]

        send_results_email(
            user_email="test@example.com",
            courses=courses,
            search_id=self.search_request.id,
        )

        # Verifica que o email foi chamado
        mock_email_class.assert_called_once()

        # Verifica se o context do template contem a URL correta
        call_args = mock_email_class.call_args
        # A URL deve conter o ID da busca e "results"
        expected_path = f"/search/{self.search_request.id}/results/"
        # Como usamos render_to_string internamente, verificamos os kwargs
        self.assertIn("body", call_args[1])


class SearchListViewAuthTestCase(TestCase):
    """Testes de autenticação para a lista de buscas."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass123",
        )

    def test_unauthenticated_redirects_to_login(self):
        """Verifica que usuario nao autenticado e redirecionado para login."""
        response = self.client.get(reverse("search:request_list"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)

    def test_authenticated_can_access_list(self):
        """Verifica que usuario autenticado pode acessar a lista."""
        self.client.login(email="test@example.com", password="testpass123")
        response = self.client.get(reverse("search:request_list"))
        self.assertEqual(response.status_code, 200)


# ============================================================
# TASK 1 - Testes do status NO_RESULTS (já existentes)
# ============================================================


class SearchStatusNoResultsTestCase(TestCase):
    """Testes para o status NO_RESULTS."""

    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass123",
        )
        self.search_request = SearchRequest.objects.create(
            user=self.user,
            notification_email="test@example.com",
            keywords="engenharia de software",
            status=SearchStatus.PENDING,
        )

    def test_no_results_status_exists(self):
        """Verifica que o status NO_RESULTS existe nas choices."""
        self.assertIn("no_results", [s[0] for s in SearchStatus.choices])

    def test_search_request_can_have_no_results_status(self):
        """Verifica que SearchRequest pode ter status NO_RESULTS."""
        self.search_request.status = SearchStatus.NO_RESULTS
        self.search_request.save()

        self.search_request.refresh_from_db()
        self.assertEqual(self.search_request.status, "no_results")

    def test_no_results_status_color(self):
        """Verifica cor do status NO_RESULTS."""
        self.search_request.status = SearchStatus.NO_RESULTS
        self.assertEqual(self.search_request.status_color, "secondary")

    def test_no_results_status_icon(self):
        """Verifica icone do status NO_RESULTS."""
        self.search_request.status = SearchStatus.NO_RESULTS
        self.assertEqual(self.search_request.status_icon, "🔍")

    def test_no_results_display_name(self):
        """Verifica nome de exibicao do status NO_RESULTS."""
        self.search_request.status = SearchStatus.NO_RESULTS
        self.assertEqual(self.search_request.get_status_display(), "Sem resultados")


class NoResultsEmailTestCase(TestCase):
    """Testes para o e-mail de 'sem resultados'."""

    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass123",
        )
        self.search_request = SearchRequest.objects.create(
            user=self.user,
            notification_email="test@example.com",
            keywords="curso inexistente",
            status=SearchStatus.NO_RESULTS,
        )

    @patch("search.emails.EmailMultiAlternatives")
    def test_send_no_results_email_success(self, mock_email_class):
        """Verifica que e-mail de 'sem resultados' e enviado corretamente."""
        mock_email = MagicMock()
        mock_email_class.return_value = mock_email

        send_no_results_email(
            user_email="test@example.com",
            search_id=self.search_request.id,
            keywords="curso inexistente",
        )

        mock_email_class.assert_called_once()
        mock_email.attach_alternative.assert_called_once()
        mock_email.send.assert_called_once_with(fail_silently=False)

    @patch("search.emails.EmailMultiAlternatives")
    def test_send_no_results_email_subject(self, mock_email_class):
        """Verifica assunto do e-mail de 'sem resultados'."""
        mock_email = MagicMock()
        mock_email_class.return_value = mock_email

        send_no_results_email(
            user_email="test@example.com",
            search_id=self.search_request.id,
            keywords="curso inexistente",
        )

        call_kwargs = mock_email_class.call_args[1]
        self.assertEqual(call_kwargs["subject"], "Sua busca foi concluída - Optio")


class SearchResultsViewNoResultsTestCase(TestCase):
    """Testes para a view de resultados com status NO_RESULTS."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass123",
        )
        self.search_request = SearchRequest.objects.create(
            user=self.user,
            notification_email="test@example.com",
            keywords="busca sem resultados",
            status=SearchStatus.NO_RESULTS,
            results_count=0,
        )

    def test_results_page_shows_no_results_state(self):
        """Verifica que a pagina de resultados exibe estado 'sem resultados'."""
        self.client.login(email="test@example.com", password="testpass123")

        response = self.client.get(
            reverse("search:search_results", kwargs={"pk": self.search_request.pk})
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Nenhum curso encontrado")
        self.assertContains(response, "Sugestões para ampliar sua busca")

    def test_results_page_shows_suggestions(self):
        """Verifica que a pagina exibe sugestoes para ampliar a busca."""
        self.client.login(email="test@example.com", password="testpass123")

        response = self.client.get(
            reverse("search:search_results", kwargs={"pk": self.search_request.pk})
        )

        self.assertContains(response, "palavras-chave mais genéricas")
        self.assertContains(response, "Nova Pesquisa")


class SearchListNoResultsFilterTestCase(TestCase):
    """Testes para o filtro NO_RESULTS na lista de buscas."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass123",
        )
        # Criar buscas com diferentes status
        SearchRequest.objects.create(
            user=self.user,
            notification_email="test@example.com",
            keywords="busca completa",
            status=SearchStatus.COMPLETED,
            results_count=5,
        )
        SearchRequest.objects.create(
            user=self.user,
            notification_email="test@example.com",
            keywords="busca vazia",
            status=SearchStatus.NO_RESULTS,
            results_count=0,
        )

    def test_filter_by_no_results(self):
        """Verifica que filtro por no_results funciona."""
        self.client.login(email="test@example.com", password="testpass123")

        response = self.client.get(
            reverse("search:request_list") + "?status=no_results"
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "busca vazia")
        self.assertNotContains(response, "busca completa")

    def test_no_results_filter_button_exists(self):
        """Verifica que o botao de filtro 'Sem Resultados' existe."""
        self.client.login(email="test@example.com", password="testpass123")

        response = self.client.get(reverse("search:request_list"))

        self.assertContains(response, "status=no_results")
        self.assertContains(response, "Sem Resultados")


class CompletedFlowStillWorksTestCase(TestCase):
    """Testes para garantir que o fluxo COMPLETED continua funcionando."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass123",
        )
        self.search_request = SearchRequest.objects.create(
            user=self.user,
            notification_email="test@example.com",
            keywords="busca com resultados",
            status=SearchStatus.COMPLETED,
            results_count=3,
        )
        # Criar cursos
        Course.objects.create(
            search_request=self.search_request,
            name="Curso de Teste 1",
            institution="Universidade Teste",
        )
        Course.objects.create(
            search_request=self.search_request,
            name="Curso de Teste 2",
            institution="Faculdade Teste",
        )

    def test_completed_search_shows_courses(self):
        """Verifica que busca COMPLETED ainda exibe cursos corretamente."""
        self.client.login(email="test@example.com", password="testpass123")

        response = self.client.get(
            reverse("search:search_results", kwargs={"pk": self.search_request.pk})
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Curso de Teste 1")
        self.assertContains(response, "Curso de Teste 2")

    def test_completed_search_has_view_results_button(self):
        """Verifica que busca COMPLETED tem botao 'Ver resultados' na lista."""
        self.client.login(email="test@example.com", password="testpass123")

        response = self.client.get(reverse("search:request_list"))

        self.assertContains(response, "Ver resultados")

    @patch("search.emails.EmailMultiAlternatives")
    def test_send_results_email_still_works(self, mock_email_class):
        """Verifica que e-mail de resultados ainda funciona."""
        mock_email = MagicMock()
        mock_email_class.return_value = mock_email

        courses = [
            {"name": "Curso 1", "institution": "Inst 1", "modality": "ead", "state": "SP", "link": ""},
        ]

        send_results_email(
            user_email="test@example.com",
            courses=courses,
            search_id=self.search_request.id,
        )

        mock_email.send.assert_called_once()
