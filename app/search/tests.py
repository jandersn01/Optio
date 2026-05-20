from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from unittest.mock import patch, MagicMock

from search.models import SearchRequest, Course
from search.choices import SearchStatus
from search.emails import send_no_results_email, send_results_email


User = get_user_model()


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
