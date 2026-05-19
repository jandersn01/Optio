from django.db import models
from .choices import SearchModality, SearchStatus, SearchStates_Br, SearchArea
from django.conf import settings

# Create your models here.

class SearchRequest(models.Model):

     user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="search_requests",
        verbose_name="Usuário",
    )

     notification_email = models.EmailField(
        verbose_name="E-mail para notificação",
    )

     keywords = models.CharField(
        max_length=255,
        verbose_name="Palavras-chave",
    )

     area = models.CharField(
        max_length=100,
        choices=SearchArea.choices,
        blank=True,
        verbose_name="Área do conhecimento",
    )

     modality = models.CharField(
        max_length=20,
        choices=SearchModality.choices,
        blank=True,
        verbose_name="Modalidade",
    )

     state = models.CharField(
        max_length=2,
        choices=SearchStates_Br.choices,
        blank=True,
        verbose_name="Estado",
    )

     status = models.CharField(
        max_length=20,
        choices=SearchStatus.choices,
        default=SearchStatus.PENDING,
        verbose_name="Status",
    )

     created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Criado em",
    )

     updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Atualizado em",
    )

     results_count = models.PositiveIntegerField(
         default=0,
         verbose_name="Quantidade de resultados",
      )

     # ══════════════════════════════════════════════════════════════
     # NOVOS CAMPOS - Fase 1 do redesign
     # ══════════════════════════════════════════════════════════════

     protocol = models.CharField(
         max_length=20,
         unique=True,
         blank=True,
         null=True,
         verbose_name="Protocolo",
     )

     result_payload = models.JSONField(
         default=list,
         blank=True,
         verbose_name="Resultados (JSON)",
     )

     error_ref = models.CharField(
         max_length=200,
         blank=True,
         default="",
         verbose_name="Referência de erro",
     )

     class Meta:
        verbose_name = "Requisição de busca"
        verbose_name_plural = "Requisições de busca"
        ordering = ["-created_at"]

     def save(self, *args, **kwargs):
         """Gera protocol automaticamente se não existir."""
         if not self.protocol:
             from django.utils import timezone
             import uuid
             short_id = uuid.uuid4().hex[:4].upper()
             self.protocol = f"OPT-{timezone.now().year}-{short_id}"
         super().save(*args, **kwargs)

     def __str__(self):
        return f"SearchRequest #{self.id} - {self.keywords}"

     @property
     def status_color(self):
      colors = {
         "pending": "warning",
         "processing": "info",
         "completed": "success",
         "failed": "danger",
         "no_results": "secondary",
         "expired": "dark",
      }
      return colors.get(self.status, "secondary")


     @property
     def status_icon(self):
      icons = {
         "pending": "⏳",
         "processing": "🔄",
         "completed": "✅",
         "failed": "❌",
         "no_results": "🔍",
         "expired": "⏰",
      }
      return icons.get(self.status, "•")

     # ══════════════════════════════════════════════════════════════
     # ALIASES - Compatibilidade com templates do redesign
     # Templates usam nomes diferentes, estas properties fazem a ponte
     # ══════════════════════════════════════════════════════════════

     @property
     def keyword(self):
         """Alias: template usa 'keyword', model usa 'keywords'."""
         return self.keywords

     @property
     def email(self):
         """Alias: template usa 'email', model usa 'notification_email'."""
         return self.notification_email

     @property
     def estado(self):
         """Alias: template usa 'estado', model usa 'state'."""
         return self.state

     @property
     def modalidade(self):
         """Alias: template usa 'modalidade', model usa 'modality'."""
         return self.modality

     @property
     def area_list(self):
         """Lista de áreas para iteração em templates."""
         if self.area:
             return [self.get_area_display()]
         return []

     @property
     def modalidade_list(self):
         """Lista de modalidades para iteração em templates."""
         if self.modality:
             return [self.get_modality_display()]
         return []

     # ══════════════════════════════════════════════════════════════
     # PROPERTIES PARA UI - Progresso e timeline
     # ══════════════════════════════════════════════════════════════

     @property
     def progress(self):
         """Porcentagem de progresso visual."""
         mapping = {
             "pending": 10,
             "processing": 50,
             "completed": 100,
             "no_results": 100,
             "failed": 100,
             "expired": 100,
         }
         return mapping.get(self.status, 0)

     @property
     def eta_minutes(self):
         """Estimativa de tempo restante."""
         return max(1, int((100 - self.progress) / 10))

     @property
     def timeline(self):
         """Timeline de etapas para exibição visual."""
         steps = [
             "Solicitação recebida",
             "Na fila de processamento",
             "Buscando em fontes",
             "Análise concluída",
             "Notificação enviada",
         ]

         # Define qual etapa está ativa baseado no status
         status_to_step = {
             "pending": 0,
             "processing": 2,
             "completed": 4,
             "no_results": 4,
             "failed": 2,
             "expired": 4,
         }

         current_step = status_to_step.get(self.status, 0)

         result = []
         for i, label in enumerate(steps):
             if self.status in ["completed", "no_results"]:
                 state = "done"
             elif self.status == "failed":
                 state = "done" if i <= 1 else "failed"
             elif i < current_step:
                 state = "done"
             elif i == current_step:
                 state = "active"
             else:
                 state = "pending"

             if state == "done":
                 time_str = self.created_at.strftime("%H:%M")
             elif state == "active":
                 time_str = "agora"
             else:
                 time_str = "—"

             result.append({
                 "label": label,
                 "state": state,
                 "time": time_str,
             })

         return result

     # ══════════════════════════════════════════════════════════════
     # HELPERS - Métodos utilitários para templates
     # ══════════════════════════════════════════════════════════════

     def is_done(self):
         """Verifica se busca está concluída."""
         return self.status == "completed"

     def is_processing(self):
         """Verifica se busca está em processamento."""
         return self.status in ["pending", "processing"]

     def is_failed(self):
         """Verifica se busca falhou."""
         return self.status == "failed"

     def has_no_results(self):
         """Verifica se busca terminou sem resultados."""
         return self.status == "no_results"
