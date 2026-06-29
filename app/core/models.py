import hashlib
import re

from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager


def _normalize_text(value: str) -> str:
    """Minúsculas, sem espaços nas pontas e com espaços internos colapsados."""
    return re.sub(r'\s+', ' ', (value or '').strip().lower())


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
    
    policy_accepted = models.BooleanField(
        default= False,
        verbose_name='Aceitou a política de Privacidade',
        help_text='Indica se o usuário aceitou a política de privacidade no momento do cadastro'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'

    def __str__(self):
        return self.email


class NotificationPreference(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notification_preference',
        verbose_name='Usuário',
    )
    area = models.TextField(
        blank=True,
        default='',
        verbose_name='Áreas de interesse',
        help_text='Valores separados por vírgula',
    )
    modality = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Modalidade preferida',
    )
    active = models.BooleanField(
        default=True,
        verbose_name='Notificações ativas',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Preferência de notificação'
        verbose_name_plural = 'Preferências de notificação'

    @property
    def area_list(self) -> list[str]:
        return [a.strip() for a in self.area.split(',') if a.strip()]

    def __str__(self):
        return f'Preferência de {self.user.email}'


class NotificationSent(models.Model):
    """Registra cada curso já notificado a um usuário, para evitar reenvios.

    Como `Course` está sempre atrelado a um `SearchRequest` (não há catálogo
    global), a deduplicação usa um fingerprint estável de nome + instituição.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications_sent',
        verbose_name='Usuário',
    )
    course_fingerprint = models.CharField(
        max_length=64,
        db_index=True,
        verbose_name='Fingerprint do curso',
    )
    course_name = models.CharField(max_length=255, verbose_name='Nome do curso')
    course_institution = models.CharField(max_length=255, verbose_name='Instituição')
    course_link = models.URLField(blank=True, verbose_name='Link')
    sent_at = models.DateTimeField(auto_now_add=True, verbose_name='Notificado em')

    class Meta:
        verbose_name = 'Notificação enviada'
        verbose_name_plural = 'Notificações enviadas'
        ordering = ['-sent_at']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'course_fingerprint'],
                name='unique_user_course_notification',
            )
        ]

    @staticmethod
    def fingerprint_for(name: str, institution: str) -> str:
        base = f'{_normalize_text(name)}|{_normalize_text(institution)}'
        return hashlib.sha256(base.encode('utf-8')).hexdigest()

    def __str__(self):
        return f'{self.course_name} → {self.user.email}'
