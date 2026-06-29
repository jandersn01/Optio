"""Testes dos jobs de notificação.

A lógica vive em `worker/domain/use_cases.py` (PreferenceNotifier / AlertNotifier),
fora dos apps Django, então o diretório do worker é adicionado ao path. As
use-cases são testadas com dublês (finder/repo/notifier fakes); o
`NotificationRepository` real é testado contra o banco.
"""
import os
import sys

from django.test import TestCase

WORKER_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', '..', 'worker')
)
if WORKER_DIR not in sys.path:
    sys.path.insert(0, WORKER_DIR)

from domain.contracts import (
    AlertSpec, CourseData, PreferenceGroup, Recipient, SearchCriteria, UserAlerts,
)
from domain.use_cases import AlertNotifier, PreferenceNotifier

from core.models import CustomUser, NotificationPreference, NotificationSent
from search.models import SavedAlert


# ── Dublês ──

class _FakeFinder:
    def __init__(self, courses):
        self._courses = courses
        self.calls = []

    def find(self, criteria):
        self.calls.append(criteria)
        return list(self._courses)


class _RecordingNotifier:
    def __init__(self):
        self.new_courses = []   # [(email, [CourseData])]
        self.digests = []       # [(email, [DigestSection])]

    def send_new_courses(self, email, courses):
        self.new_courses.append((email, courses))

    def send_alerts_digest(self, email, sections):
        self.digests.append((email, sections))


class _FakeRepo:
    """Repo em memória: dedup por (user_id, fingerprint=name)."""
    def __init__(self, groups=None, user_alerts=None):
        self._groups = groups or []
        self._user_alerts = user_alerts or []
        self.sent = set()
        self.checked = []

    def preference_groups(self):
        return self._groups

    def users_with_active_alerts(self):
        return self._user_alerts

    def filter_new(self, user_id, courses):
        seen, out = set(), []
        for c in courses:
            if c.name in seen or (user_id, c.name) in self.sent:
                continue
            seen.add(c.name)
            out.append(c)
        return out

    def record_sent(self, user_id, courses):
        for c in courses:
            self.sent.add((user_id, c.name))

    def mark_alerts_checked(self, ids):
        self.checked.extend(ids)


def _course(name, institution='IFPB'):
    return CourseData(name=name, institution=institution, modality='ead', state='PB', link='http://x')


# ── PreferenceNotifier ──

class PreferenceNotifierTests(TestCase):
    def setUp(self):
        self.group = PreferenceGroup(
            criteria=SearchCriteria(keywords='exatas', area='exatas'),
            recipients=[Recipient(id=1, email='a@x.com'), Recipient(id=2, email='b@x.com')],
        )

    def test_notifica_cada_usuario_do_grupo(self):
        repo = _FakeRepo(groups=[self.group])
        notifier = _RecordingNotifier()
        PreferenceNotifier(_FakeFinder([_course('Curso A')]), repo, notifier).run()
        self.assertEqual(len(notifier.new_courses), 2)
        self.assertEqual({e for e, _ in notifier.new_courses}, {'a@x.com', 'b@x.com'})

    def test_nao_reenvia_curso_ja_enviado(self):
        repo = _FakeRepo(groups=[self.group])
        notifier = _RecordingNotifier()
        finder = _FakeFinder([_course('Curso A')])
        PreferenceNotifier(finder, repo, notifier).run()
        PreferenceNotifier(finder, repo, notifier).run()
        self.assertEqual(len(notifier.new_courses), 2)  # só a 1ª execução envia

    def test_grupo_sem_cursos_nao_envia(self):
        repo = _FakeRepo(groups=[self.group])
        notifier = _RecordingNotifier()
        PreferenceNotifier(_FakeFinder([]), repo, notifier).run()
        self.assertEqual(notifier.new_courses, [])


# ── AlertNotifier ──

class AlertNotifierTests(TestCase):
    def setUp(self):
        self.user_alerts = UserAlerts(
            recipient=Recipient(id=1, email='aluno@x.com'),
            alerts=[
                AlertSpec(id=10, name='IA', criteria=SearchCriteria(keywords='ia')),
                AlertSpec(id=11, name='Dados', criteria=SearchCriteria(keywords='dados')),
            ],
        )

    def test_envia_digest_com_secoes_por_alerta(self):
        repo = _FakeRepo(user_alerts=[self.user_alerts])
        notifier = _RecordingNotifier()
        AlertNotifier(_FakeFinder([_course('Mestrado em IA')]), repo, notifier).run()
        self.assertEqual(len(notifier.digests), 1)
        email, sections = notifier.digests[0]
        self.assertEqual(email, 'aluno@x.com')
        # mesmo curso nos dois alertas → dedup cross-alerta deixa só 1 seção com conteúdo
        self.assertEqual(len(sections), 1)
        self.assertEqual(sections[0].alert_name, 'IA')
        self.assertEqual(repo.checked, [10, 11])

    def test_nao_reenvia_no_segundo_ciclo(self):
        repo = _FakeRepo(user_alerts=[self.user_alerts])
        notifier = _RecordingNotifier()
        finder = _FakeFinder([_course('Mestrado em IA')])
        AlertNotifier(finder, repo, notifier).run()
        AlertNotifier(finder, repo, notifier).run()
        self.assertEqual(len(notifier.digests), 1)


# ── NotificationRepository (integração com o banco) ──

class NotificationRepositoryTests(TestCase):
    def setUp(self):
        from infra.repositories import NotificationRepository
        self.repo = NotificationRepository()
        self.user = CustomUser.objects.create_user(email='u@x.com', password='SenhaForte123!')

    def test_preference_groups_agrupa_por_area_modalidade(self):
        NotificationPreference.objects.create(
            user=self.user, area='exatas,humanas', modality='ead', active=True
        )
        groups = self.repo.preference_groups()
        keys = {(g.criteria.area, g.criteria.modality) for g in groups}
        self.assertEqual(keys, {('exatas', 'ead'), ('humanas', 'ead')})
        self.assertEqual(groups[0].recipients[0].email, 'u@x.com')

    def test_users_with_active_alerts_ignora_pausados(self):
        SavedAlert.objects.create(user=self.user, name='A', keywords='a', active=True)
        SavedAlert.objects.create(user=self.user, name='B', keywords='b', active=False)
        users = self.repo.users_with_active_alerts()
        self.assertEqual(len(users), 1)
        self.assertEqual(len(users[0].alerts), 1)
        self.assertEqual(users[0].alerts[0].name, 'A')

    def test_filter_new_e_record_sent(self):
        courses = [_course('Curso X'), _course('Curso X'), _course('Curso Y')]  # 1 duplicado
        novos = self.repo.filter_new(self.user.id, courses)
        self.assertEqual({c.name for c in novos}, {'Curso X', 'Curso Y'})  # dedup intra-lista
        self.repo.record_sent(self.user.id, novos)
        # segunda passada: nada novo
        self.assertEqual(self.repo.filter_new(self.user.id, courses), [])
        self.assertEqual(NotificationSent.objects.filter(user=self.user).count(), 2)

    def test_mark_alerts_checked(self):
        alert = SavedAlert.objects.create(user=self.user, name='A', keywords='a', active=True)
        self.repo.mark_alerts_checked([alert.id])
        alert.refresh_from_db()
        self.assertIsNotNone(alert.last_checked_at)
