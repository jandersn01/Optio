"""Testes para search/tasks.py — fail_stalled_searches.

Task 2: Busca travada há mais de 5 minutos é marcada como FAILED.
"""
from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model

from search.models import SearchRequest
from search.choices import SearchStatus
from search.tasks import fail_stalled_searches

User = get_user_model()


class FailStalledSearchesTests(TestCase):
    """Testes do sweeper fail_stalled_searches."""

    def setUp(self):
        self.user = User.objects.create_user(
            email="user@test.com",
            password="SenhaForte123!"
        )

    def _create_search(self, status, minutes_ago):
        """Helper para criar SearchRequest com created_at no passado."""
        search = SearchRequest.objects.create(
            user=self.user,
            notification_email=self.user.email,
            keywords="teste",
            status=status,
        )
        # Atualiza created_at diretamente no banco para simular tempo passado
        SearchRequest.all_objects.filter(pk=search.pk).update(
            created_at=timezone.now() - timedelta(minutes=minutes_ago)
        )
        search.refresh_from_db()
        return search

    def test_pending_travada_6_minutos_marcada_failed(self):
        """Busca PENDING há mais de 5 minutos é marcada como FAILED."""
        search = self._create_search(SearchStatus.PENDING, minutes_ago=6)

        fail_stalled_searches()

        search.refresh_from_db()
        self.assertEqual(search.status, SearchStatus.FAILED)

    def test_processing_travada_6_minutos_marcada_failed(self):
        """Busca PROCESSING há mais de 5 minutos é marcada como FAILED."""
        search = self._create_search(SearchStatus.PROCESSING, minutes_ago=6)

        fail_stalled_searches()

        search.refresh_from_db()
        self.assertEqual(search.status, SearchStatus.FAILED)

    def test_pending_recente_4_minutos_nao_e_mexida(self):
        """Busca PENDING há menos de 5 minutos não é alterada."""
        search = self._create_search(SearchStatus.PENDING, minutes_ago=4)

        fail_stalled_searches()

        search.refresh_from_db()
        self.assertEqual(search.status, SearchStatus.PENDING)

    def test_processing_recente_3_minutos_nao_e_mexida(self):
        """Busca PROCESSING há menos de 5 minutos não é alterada."""
        search = self._create_search(SearchStatus.PROCESSING, minutes_ago=3)

        fail_stalled_searches()

        search.refresh_from_db()
        self.assertEqual(search.status, SearchStatus.PROCESSING)

    def test_completed_antiga_nao_e_mexida(self):
        """Busca COMPLETED antiga não é alterada (só PENDING/PROCESSING)."""
        search = self._create_search(SearchStatus.COMPLETED, minutes_ago=60)

        fail_stalled_searches()

        search.refresh_from_db()
        self.assertEqual(search.status, SearchStatus.COMPLETED)

    def test_failed_antiga_nao_e_mexida(self):
        """Busca já FAILED não é alterada."""
        search = self._create_search(SearchStatus.FAILED, minutes_ago=60)

        fail_stalled_searches()

        search.refresh_from_db()
        self.assertEqual(search.status, SearchStatus.FAILED)

    def test_no_results_antiga_nao_e_mexida(self):
        """Busca NO_RESULTS antiga não é alterada."""
        search = self._create_search(SearchStatus.NO_RESULTS, minutes_ago=60)

        fail_stalled_searches()

        search.refresh_from_db()
        self.assertEqual(search.status, SearchStatus.NO_RESULTS)

    def test_limite_exato_5_minutos_nao_e_mexida(self):
        """Busca exatamente no limite de 5 minutos não é alterada."""
        search = self._create_search(SearchStatus.PENDING, minutes_ago=5)

        fail_stalled_searches()

        search.refresh_from_db()
        # O código usa created_at__lt=threshold (estritamente menor)
        # então 5 minutos exatos não é afetado
        self.assertEqual(search.status, SearchStatus.PENDING)

    def test_multiplas_buscas_travadas_sao_marcadas(self):
        """Múltiplas buscas travadas são todas marcadas como FAILED."""
        search1 = self._create_search(SearchStatus.PENDING, minutes_ago=10)
        search2 = self._create_search(SearchStatus.PROCESSING, minutes_ago=15)
        search3 = self._create_search(SearchStatus.PENDING, minutes_ago=2)  # recente

        fail_stalled_searches()

        search1.refresh_from_db()
        search2.refresh_from_db()
        search3.refresh_from_db()

        self.assertEqual(search1.status, SearchStatus.FAILED)
        self.assertEqual(search2.status, SearchStatus.FAILED)
        self.assertEqual(search3.status, SearchStatus.PENDING)  # não afetada

    def test_buscas_de_usuarios_diferentes(self):
        """Sweeper afeta buscas de todos os usuários."""
        user2 = User.objects.create_user(
            email="outro@test.com",
            password="SenhaForte123!"
        )

        search1 = self._create_search(SearchStatus.PENDING, minutes_ago=10)

        search2 = SearchRequest.objects.create(
            user=user2,
            notification_email=user2.email,
            keywords="teste user2",
            status=SearchStatus.PROCESSING,
        )
        SearchRequest.all_objects.filter(pk=search2.pk).update(
            created_at=timezone.now() - timedelta(minutes=8)
        )

        fail_stalled_searches()

        search1.refresh_from_db()
        search2.refresh_from_db()

        self.assertEqual(search1.status, SearchStatus.FAILED)
        self.assertEqual(search2.status, SearchStatus.FAILED)
