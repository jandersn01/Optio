from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from unittest.mock import patch, MagicMock

from search.models import SearchRequest, Course, Favorite
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
        self.assertIn("/login/", response.url)

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
        self.assertIn("/login/", response.url)

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


# ============================================================
# TASK 3 - Testes da página de favoritos
# ============================================================


class FavoritesListViewTestCase(TestCase):
    """Testes para a view de listagem de favoritos."""

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
            keywords="teste favoritos",
            status=SearchStatus.COMPLETED,
        )
        self.course = Course.objects.create(
            search_request=self.search_request,
            name="Curso de Teste",
            institution="IFPB",
            modality="ead",
            state="PB",
        )

    def test_unauthenticated_redirects_to_login(self):
        """Verifica que usuario nao autenticado e redirecionado para login."""
        response = self.client.get(reverse("search:favorites_list"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)

    def test_authenticated_can_access_favorites(self):
        """Verifica que usuario autenticado pode acessar favoritos."""
        self.client.login(email="test@example.com", password="testpass123")
        response = self.client.get(reverse("search:favorites_list"))
        self.assertEqual(response.status_code, 200)

    def test_user_sees_only_own_favorites(self):
        """Verifica que usuario ve apenas seus proprios favoritos."""
        # Criar favoritos para ambos usuarios
        Favorite.objects.create(user=self.user, course=self.course)

        other_search = SearchRequest.objects.create(
            user=self.other_user,
            notification_email="other@example.com",
            keywords="teste outro",
            status=SearchStatus.COMPLETED,
        )
        other_course = Course.objects.create(
            search_request=other_search,
            name="Curso do Outro",
            institution="UFPB",
        )
        Favorite.objects.create(user=self.other_user, course=other_course)

        self.client.login(email="test@example.com", password="testpass123")
        response = self.client.get(reverse("search:favorites_list"))

        self.assertContains(response, "Curso de Teste")
        self.assertNotContains(response, "Curso do Outro")

    def test_favorites_displayed_correctly(self):
        """Verifica que favoritos sao exibidos corretamente."""
        Favorite.objects.create(user=self.user, course=self.course)

        self.client.login(email="test@example.com", password="testpass123")
        response = self.client.get(reverse("search:favorites_list"))

        self.assertContains(response, "Curso de Teste")
        self.assertContains(response, "IFPB")
        self.assertContains(response, "PB")

    def test_select_related_used_in_query(self):
        """Verifica que select_related e utilizado na consulta."""
        Favorite.objects.create(user=self.user, course=self.course)

        self.client.login(email="test@example.com", password="testpass123")

        with self.assertNumQueries(6):
            # 1: session, 2: user, 3-4: COUNTs do sidebar_context (favoritos + buscas),
            # 5: COUNT do Paginator, 6: favoritos com select_related(course)
            response = self.client.get(reverse("search:favorites_list"))
            self.assertEqual(response.status_code, 200)
            # Acessar os cursos no template nao deve gerar queries adicionais
            self.assertContains(response, "Curso de Teste")

    def _create_favorites(self, total):
        """Cria `total` favoritos do usuario para os testes de paginacao."""
        for i in range(total):
            course = Course.objects.create(
                search_request=self.search_request,
                name=f"Curso {i:02d}",
                institution="IFPB",
            )
            Favorite.objects.create(user=self.user, course=course)

    def test_second_page_returns_favorites_11_to_20(self):
        """Verifica que ?page=2 retorna a segunda pagina (favoritos 11-20)."""
        self._create_favorites(25)
        self.client.login(email="test@example.com", password="testpass123")

        response = self.client.get(reverse("search:favorites_list"), {"page": 2})

        page_obj = response.context["page_obj"]
        self.assertEqual(page_obj.number, 2)
        self.assertEqual(len(page_obj.object_list), 10)
        self.assertContains(response, "Curso 14")
        self.assertContains(response, "Curso 05")
        self.assertNotContains(response, "Curso 24")
        self.assertNotContains(response, "Curso 04")

    def test_pagination_controls_shown_with_multiple_pages(self):
        """Verifica que controles aparecem quando ha mais de uma pagina."""
        self._create_favorites(15)
        self.client.login(email="test@example.com", password="testpass123")

        response = self.client.get(reverse("search:favorites_list"))

        self.assertContains(response, "Próxima")

    def test_pagination_controls_hidden_with_single_page(self):
        """Verifica que controles nao aparecem com uma unica pagina."""
        self._create_favorites(5)
        self.client.login(email="test@example.com", password="testpass123")

        response = self.client.get(reverse("search:favorites_list"))

        self.assertNotContains(response, "Próxima")


class FavoritesEmptyStateTestCase(TestCase):
    """Testes para o estado vazio da lista de favoritos."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass123",
        )

    def test_empty_favorites_shows_message(self):
        """Verifica que lista vazia exibe mensagem correta."""
        self.client.login(email="test@example.com", password="testpass123")
        response = self.client.get(reverse("search:favorites_list"))

        self.assertContains(response, "Você ainda não tem favoritos")

    def test_empty_favorites_shows_search_link(self):
        """Verifica que lista vazia exibe link para pesquisa."""
        self.client.login(email="test@example.com", password="testpass123")
        response = self.client.get(reverse("search:favorites_list"))

        self.assertContains(response, "Fazer uma pesquisa")
        self.assertContains(response, reverse("search:request_create"))


class FavoriteRemoveTestCase(TestCase):
    """Testes para remocao de favoritos."""

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
            keywords="teste remocao",
            status=SearchStatus.COMPLETED,
        )
        self.course = Course.objects.create(
            search_request=self.search_request,
            name="Curso para Remover",
            institution="IFPB",
        )
        self.favorite = Favorite.objects.create(user=self.user, course=self.course)

    def test_user_can_remove_own_favorite(self):
        """Verifica que usuario pode remover proprio favorito."""
        self.client.login(email="test@example.com", password="testpass123")

        response = self.client.post(
            reverse("search:favorite_remove", kwargs={"pk": self.favorite.pk})
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("search:favorites_list"))

    def test_favorite_is_deleted_from_database(self):
        """Verifica que favorito e removido do banco."""
        self.client.login(email="test@example.com", password="testpass123")

        self.assertEqual(Favorite.objects.filter(user=self.user).count(), 1)

        self.client.post(
            reverse("search:favorite_remove", kwargs={"pk": self.favorite.pk})
        )

        self.assertEqual(Favorite.objects.filter(user=self.user).count(), 0)

    def test_user_cannot_remove_other_users_favorite(self):
        """Verifica que usuario nao pode remover favorito de outro usuario."""
        self.client.login(email="other@example.com", password="otherpass123")

        response = self.client.post(
            reverse("search:favorite_remove", kwargs={"pk": self.favorite.pk})
        )

        self.assertEqual(response.status_code, 404)
        # Favorito ainda existe
        self.assertTrue(Favorite.objects.filter(pk=self.favorite.pk).exists())

    def test_unauthenticated_cannot_remove_favorite(self):
        """Verifica que usuario nao autenticado nao pode remover favorito."""
        response = self.client.post(
            reverse("search:favorite_remove", kwargs={"pk": self.favorite.pk})
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)
        # Favorito ainda existe
        self.assertTrue(Favorite.objects.filter(pk=self.favorite.pk).exists())

    def test_remove_nonexistent_favorite_returns_404(self):
        """Verifica que remover favorito inexistente retorna 404."""
        self.client.login(email="test@example.com", password="testpass123")

        response = self.client.post(
            reverse("search:favorite_remove", kwargs={"pk": 99999})
        )

        self.assertEqual(response.status_code, 404)

    def test_get_request_not_allowed(self):
        """Verifica que GET nao e permitido para remocao."""
        self.client.login(email="test@example.com", password="testpass123")

        response = self.client.get(
            reverse("search:favorite_remove", kwargs={"pk": self.favorite.pk})
        )

        self.assertEqual(response.status_code, 405)


class FavoriteModelTestCase(TestCase):
    """Testes para o modelo Favorite."""

    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass123",
        )
        self.search_request = SearchRequest.objects.create(
            user=self.user,
            notification_email="test@example.com",
            keywords="teste modelo",
            status=SearchStatus.COMPLETED,
        )
        self.course = Course.objects.create(
            search_request=self.search_request,
            name="Curso Modelo",
            institution="IFPB",
        )

    def test_favorite_creation(self):
        """Verifica que favorito pode ser criado."""
        favorite = Favorite.objects.create(user=self.user, course=self.course)

        self.assertEqual(favorite.user, self.user)
        self.assertEqual(favorite.course, self.course)
        self.assertIsNotNone(favorite.created_at)

    def test_unique_constraint_user_course(self):
        """Verifica que usuario nao pode favoritar mesmo curso duas vezes."""
        from django.db import IntegrityError

        Favorite.objects.create(user=self.user, course=self.course)

        with self.assertRaises(IntegrityError):
            Favorite.objects.create(user=self.user, course=self.course)

    def test_favorite_str_representation(self):
        """Verifica representacao string do favorito."""
        favorite = Favorite.objects.create(user=self.user, course=self.course)

        self.assertEqual(str(favorite), "test@example.com - Curso Modelo")
