"""Testes dos serviços de alertas salvos (criação a partir de busca, limite,
duplicata, toggle e exclusão)."""
from django.test import TestCase
from django.contrib.auth import get_user_model

from search.models import SavedAlert
from search import services

User = get_user_model()


class AlertServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='aluno@example.com', password='SenhaForte123!')

    def _data(self, keywords='engenharia de software', area='engenharias',
              modality='presencial', state='PB'):
        return {'keywords': keywords, 'area': area, 'modality': modality, 'state': state}

    def test_cria_alerta(self):
        alert, reason = services.create_alert_from_search(self.user, self._data())
        self.assertEqual(reason, 'created')
        self.assertIsNotNone(alert)
        self.assertTrue(alert.active)
        self.assertEqual(SavedAlert.objects.filter(user=self.user).count(), 1)

    def test_nao_duplica_alerta_ativo(self):
        services.create_alert_from_search(self.user, self._data())
        alert, reason = services.create_alert_from_search(self.user, self._data())
        self.assertEqual(reason, 'duplicate')
        self.assertIsNone(alert)
        self.assertEqual(SavedAlert.objects.filter(user=self.user).count(), 1)

    def test_respeita_limite_de_ativos(self):
        for i in range(services.MAX_ACTIVE_ALERTS_PER_USER):
            _, reason = services.create_alert_from_search(self.user, self._data(keywords=f'busca {i}'))
            self.assertEqual(reason, 'created')
        alert, reason = services.create_alert_from_search(self.user, self._data(keywords='excedente'))
        self.assertEqual(reason, 'limit')
        self.assertIsNone(alert)

    def test_toggle_pausa_e_reativa(self):
        alert, _ = services.create_alert_from_search(self.user, self._data())
        a, toggled = services.toggle_alert(self.user, alert.pk)
        self.assertTrue(toggled)
        self.assertFalse(a.active)
        a, toggled = services.toggle_alert(self.user, alert.pk)
        self.assertTrue(toggled)
        self.assertTrue(a.active)

    def test_toggle_bloqueado_ao_atingir_limite(self):
        for i in range(services.MAX_ACTIVE_ALERTS_PER_USER):
            services.create_alert_from_search(self.user, self._data(keywords=f'a{i}'))
        paused = SavedAlert.objects.create(
            user=self.user, name='pausado', keywords='pausado', active=False
        )
        a, toggled = services.toggle_alert(self.user, paused.pk)
        self.assertFalse(toggled)
        paused.refresh_from_db()
        self.assertFalse(paused.active)

    def test_apaga_alerta(self):
        alert, _ = services.create_alert_from_search(self.user, self._data())
        services.delete_alert(self.user, alert.pk)
        self.assertFalse(SavedAlert.objects.filter(pk=alert.pk).exists())
