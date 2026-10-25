from django.core import mail
from django.test import SimpleTestCase, override_settings

from core.emails import EmailDeliveryError, send_new_courses_email


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
)
class NewCoursesEmailTests(SimpleTestCase):
    def setUp(self):
        self.courses = [{
            "name": "Mestrado em Computação",
            "institution": "IFPB",
            "modality": "ead",
            "state": "PB",
            "link": "https://example.test/curso",
        }]

    def test_envia_conteudo_para_destinatario_correto(self):
        send_new_courses_email("aluno@example.test", self.courses)

        self.assertEqual(len(mail.outbox), 1)
        message = mail.outbox[0]
        self.assertEqual(message.to, ["aluno@example.test"])
        self.assertIn("Mestrado em Computação", message.body)
        self.assertIn("IFPB", message.body)
        self.assertEqual(message.alternatives[0].mimetype, "text/html")
        self.assertIn(
            "https://example.test/curso",
            message.alternatives[0].content,
        )

    def test_lista_vazia_nao_envia(self):
        send_new_courses_email("aluno@example.test", [])

        self.assertEqual(len(mail.outbox), 0)

    def test_destinatario_ausente_gera_erro(self):
        with self.assertRaises(EmailDeliveryError):
            send_new_courses_email("", self.courses)

        self.assertEqual(len(mail.outbox), 0)