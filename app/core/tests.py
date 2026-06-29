from django.test import TestCase
from django.urls import reverse
from .models import CustomUser, NotificationPreference


class CadastroTests(TestCase):
    def setUp(self):
        self.url = reverse('core:cadastro')
        self.dados_validos = {
            'nome': 'João Silva',
            'email': 'joao@example.com',
            'password1': 'SenhaForte123!',
            'password2': 'SenhaForte123!',
            'policy_accepted': True,
        }

    def test_get_exibe_formulario(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/register.html')

    def test_cadastro_valido_cria_usuario(self):
        response = self.client.post(self.url, self.dados_validos)
        self.assertRedirects(response, reverse('login'))
        self.assertTrue(CustomUser.objects.filter(email='joao@example.com').exists())
        usuario = CustomUser.objects.get(email='joao@example.com')
        self.assertEqual(usuario.first_name, 'João Silva')

    def test_cadastro_valido_salva_senha_com_hash(self):
        self.client.post(self.url, self.dados_validos)
        usuario = CustomUser.objects.get(email='joao@example.com')
        self.assertTrue(usuario.check_password('SenhaForte123!'))
        self.assertNotEqual(usuario.password, 'SenhaForte123!')

    def test_email_duplicado_exibe_erro(self):
        CustomUser.objects.create_user(email='joao@example.com', password='SenhaForte123!')
        response = self.client.post(self.url, self.dados_validos)
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertIn('email', form.errors)
        self.assertIn('Este e-mail já está cadastrado.', form.errors['email'])

    def test_senha_muito_curta_exibe_erro(self):
        dados = {**self.dados_validos, 'password1': 'abc123', 'password2': 'abc123'}
        response = self.client.post(self.url, dados)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(CustomUser.objects.filter(email='joao@example.com').exists())
        self.assertIn('password2', response.context['form'].errors)

    def test_senhas_diferentes_exibe_erro(self):
        dados = {**self.dados_validos, 'password2': 'SenhaDiferente456!'}
        response = self.client.post(self.url, dados)
        self.assertEqual(response.status_code, 200)
        self.assertIn('password2', response.context['form'].errors)

    def test_usuario_ja_autenticado_redireciona(self):
        CustomUser.objects.create_user(email='joao@example.com', password='SenhaForte123!')
        self.client.login(email='joao@example.com', password='SenhaForte123!')
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('core:dashboard'))


class NotificationPreferenceTests(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email='pref@example.com',
            password='SenhaForte123!',
            first_name='Maria',
        )
        self.client.login(email='pref@example.com', password='SenhaForte123!')
        self.url = reverse('core:preferences')

    def test_get_exibe_formulario(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/preferences.html')

    def test_get_cria_preferencia_se_nao_existir(self):
        self.client.get(self.url)
        self.assertTrue(NotificationPreference.objects.filter(user=self.user).exists())

    def test_salva_preferencias(self):
        response = self.client.post(self.url, {
            'first_name': 'Maria',
            'email': 'pref@example.com',
            'area': 'exatas',
            'modality': 'ead',
            'active': 'on',
        })
        self.assertRedirects(response, self.url)
        pref = NotificationPreference.objects.get(user=self.user)
        self.assertEqual(pref.area, 'exatas')
        self.assertEqual(pref.modality, 'ead')
        self.assertTrue(pref.active)

    def test_toggle_desativa_notificacao(self):
        NotificationPreference.objects.create(user=self.user, active=True)
        # sem 'area' = lista vazia (nenhuma área selecionada)
        # sem 'active' = False no BooleanField de checkbox
        self.client.post(self.url, {
            'first_name': 'Maria',
            'email': 'pref@example.com',
            'modality': '',
        })
        pref = NotificationPreference.objects.get(user=self.user)
        self.assertFalse(pref.active)

    def test_toggle_ativa_notificacao(self):
        NotificationPreference.objects.create(user=self.user, active=False)
        self.client.post(self.url, {
            'first_name': 'Maria',
            'email': 'pref@example.com',
            'modality': '',
            'active': 'on',
        })
        pref = NotificationPreference.objects.get(user=self.user)
        self.assertTrue(pref.active)

    def test_pagina_exige_autenticacao(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, f'/login/?next={self.url}')
