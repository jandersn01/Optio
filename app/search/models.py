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
     
     class Meta:
        verbose_name = "Requisição de busca"
        verbose_name_plural = "Requisições de busca"
        ordering = ["-created_at"]



     def __str__(self):
        return f"SearchRequest #{self.id} - {self.keywords}"
     
     @property
     def status_color(self):
      colors = {
         "pending": "warning",
         "processing": "info",
         "completed": "success",
         "failed": "danger",
      }
      return colors.get(self.status, "secondary")


     @property
     def status_icon(self):
      icons = {
         "pending": "⏳",
         "processing": "🔄",
         "completed": "✅",
         "failed": "❌",
      }
      return icons.get(self.status, "•")