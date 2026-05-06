from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.conf import settings


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('O e-mail é obrigatório.')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if not extra_fields.get('is_staff'):
            raise ValueError('Superusuário precisa ter is_staff=True.')
        if not extra_fields.get('is_superuser'):
            raise ValueError('Superusuário precisa ter is_superuser=True.')
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    username = None
    email = models.EmailField('E-mail', unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'

    def __str__(self):
        return self.email


class SearchRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pendente'
        PROCESSING = 'processing', 'Em Andamento'
        COMPLETED = 'completed', 'Concluída'
        FAILED = 'failed', 'Falhou'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='core_search_requests',
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
