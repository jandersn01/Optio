"""Testes para search/forms.py — SearchRequestForm.

Tasks 5 e 6: Filtros de modalidade e estado/região no formulário de busca.
"""
from django.test import TestCase

from search.forms import SearchRequestForm
from search.choices import SearchModality, SearchStates_Br


class SearchRequestFormModalityTests(TestCase):
    """SearchRequestForm aceita modalidades válidas e rejeita inválidas."""

    def _form_data(self, modality="", state="", keywords="engenharia de software"):
        """Helper para criar dados do formulário."""
        return {
            "keywords": keywords,
            "area": "",
            "modality": modality,
            "state": state,
        }

    def test_modality_vazio_e_aceito(self):
        """Modalidade vazia (todas) é aceita."""
        form = SearchRequestForm(data=self._form_data(modality=""))
        self.assertTrue(form.is_valid(), form.errors)

    def test_modality_ead_e_aceito(self):
        """Modalidade 'ead' é aceita."""
        form = SearchRequestForm(data=self._form_data(modality="ead"))
        self.assertTrue(form.is_valid(), form.errors)

    def test_modality_presencial_e_aceito(self):
        """Modalidade 'presencial' é aceita."""
        form = SearchRequestForm(data=self._form_data(modality="presencial"))
        self.assertTrue(form.is_valid(), form.errors)

    def test_modality_hibrido_e_aceito(self):
        """Modalidade 'hibrido' é aceita."""
        form = SearchRequestForm(data=self._form_data(modality="hibrido"))
        self.assertTrue(form.is_valid(), form.errors)

    def test_modality_invalida_e_rejeitada(self):
        """Modalidade fora do domínio é rejeitada."""
        form = SearchRequestForm(data=self._form_data(modality="semi-presencial"))
        self.assertFalse(form.is_valid())
        self.assertIn("modality", form.errors)

    def test_modality_online_e_rejeitada(self):
        """Modalidade 'online' (não existe no enum) é rejeitada."""
        form = SearchRequestForm(data=self._form_data(modality="online"))
        self.assertFalse(form.is_valid())
        self.assertIn("modality", form.errors)


class SearchRequestFormStateTests(TestCase):
    """SearchRequestForm aceita estados válidos e rejeita inválidos."""

    def _form_data(self, state="", modality="", keywords="engenharia de software"):
        """Helper para criar dados do formulário."""
        return {
            "keywords": keywords,
            "area": "",
            "modality": modality,
            "state": state,
        }

    def test_state_vazio_e_aceito(self):
        """Estado vazio (todo o Brasil) é aceito."""
        form = SearchRequestForm(data=self._form_data(state=""))
        self.assertTrue(form.is_valid(), form.errors)

    def test_state_pb_e_aceito(self):
        """Estado 'PB' (Paraíba) é aceito."""
        form = SearchRequestForm(data=self._form_data(state="PB"))
        self.assertTrue(form.is_valid(), form.errors)

    def test_state_sp_e_aceito(self):
        """Estado 'SP' (São Paulo) é aceito."""
        form = SearchRequestForm(data=self._form_data(state="SP"))
        self.assertTrue(form.is_valid(), form.errors)

    def test_state_df_e_aceito(self):
        """Estado 'DF' (Distrito Federal) é aceito."""
        form = SearchRequestForm(data=self._form_data(state="DF"))
        self.assertTrue(form.is_valid(), form.errors)

    def test_state_invalido_e_rejeitado(self):
        """Estado fora do domínio é rejeitado."""
        form = SearchRequestForm(data=self._form_data(state="XX"))
        self.assertFalse(form.is_valid())
        self.assertIn("state", form.errors)

    def test_state_lowercase_e_rejeitado(self):
        """Estado em minúsculo é rejeitado (modelo espera uppercase)."""
        form = SearchRequestForm(data=self._form_data(state="pb"))
        self.assertFalse(form.is_valid())
        self.assertIn("state", form.errors)

    def test_state_nome_completo_e_rejeitado(self):
        """Nome completo do estado é rejeitado (espera sigla)."""
        form = SearchRequestForm(data=self._form_data(state="Paraíba"))
        self.assertFalse(form.is_valid())
        self.assertIn("state", form.errors)


class SearchRequestFormKeywordsTests(TestCase):
    """SearchRequestForm valida keywords com mínimo de 3 caracteres."""

    def _form_data(self, keywords=""):
        """Helper para criar dados do formulário."""
        return {
            "keywords": keywords,
            "area": "",
            "modality": "",
            "state": "",
        }

    def test_keywords_vazio_e_rejeitado(self):
        """Keywords vazio é rejeitado."""
        form = SearchRequestForm(data=self._form_data(keywords=""))
        self.assertFalse(form.is_valid())
        self.assertIn("keywords", form.errors)

    def test_keywords_2_chars_e_rejeitado(self):
        """Keywords com 2 caracteres é rejeitado."""
        form = SearchRequestForm(data=self._form_data(keywords="ab"))
        self.assertFalse(form.is_valid())
        self.assertIn("keywords", form.errors)

    def test_keywords_3_chars_e_aceito(self):
        """Keywords com 3 caracteres é aceito."""
        form = SearchRequestForm(data=self._form_data(keywords="abc"))
        self.assertTrue(form.is_valid(), form.errors)

    def test_keywords_com_espacos_e_trimado(self):
        """Keywords com espaços é trimado antes da validação."""
        form = SearchRequestForm(data=self._form_data(keywords="  ab  "))
        # Após trim, sobra "ab" (2 chars) — deve ser rejeitado
        self.assertFalse(form.is_valid())
        self.assertIn("keywords", form.errors)

    def test_keywords_longo_e_aceito(self):
        """Keywords longo é aceito."""
        form = SearchRequestForm(data=self._form_data(keywords="engenharia de software"))
        self.assertTrue(form.is_valid(), form.errors)
