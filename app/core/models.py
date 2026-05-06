from django.db import models
from django.contrib.auth.models import User


class SearchRequest(models.Model):
    """
    Modelo para armazenar requisições de pesquisa de cursos.
    Preparado para integração com o worker RabbitMQ.
    """

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pendente'
        PROCESSING = 'processing', 'Em Andamento'
        COMPLETED = 'completed', 'Concluída'
        FAILED = 'failed', 'Falhou'

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='search_requests',
        verbose_name='Usuário'
    )
    query = models.CharField(
        max_length=500,
        verbose_name='Termo de busca'
    )
    area = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name='Área de conhecimento'
    )
    modality = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='Modalidade'
    )
    state = models.CharField(
        max_length=2,
        blank=True,
        null=True,
        verbose_name='Estado'
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name='Status'
    )
    results_count = models.IntegerField(
        default=0,
        verbose_name='Quantidade de resultados'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Criado em'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Atualizado em'
    )

    class Meta:
        verbose_name = 'Requisição de Pesquisa'
        verbose_name_plural = 'Requisições de Pesquisa'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.query} - {self.get_status_display()}"

    @property
    def status_color(self):
        """Retorna a cor CSS para o status atual."""
        colors = {
            'pending': 'warning',
            'processing': 'info',
            'completed': 'success',
            'failed': 'danger',
        }
        return colors.get(self.status, 'secondary')

    @property
    def status_icon(self):
        """Retorna o ícone para o status atual."""
        icons = {
            'pending': '⏳',
            'processing': '🔄',
            'completed': '✅',
            'failed': '❌',
        }
        return icons.get(self.status, '•')
