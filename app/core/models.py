from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _


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
    email = models.EmailField(_('E-mail'), unique=True)

    policy_accepted = models.BooleanField(
        default= False,
        verbose_name=_('Aceitou a política de Privacidade'),
        help_text=_('Indica se o usuário aceitou a política de privacidade no momento do cadastro')
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    class Meta:
        verbose_name = _('Usuário')
        verbose_name_plural = _('Usuários')

    def __str__(self):
        return self.email


class NotificationPreference(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notification_preference',
        verbose_name=_('Usuário'),
    )
    area = models.TextField(
        blank=True,
        default='',
        verbose_name=_('Áreas de interesse'),
        help_text=_('Valores separados por vírgula'),
    )
    modality = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_('Modalidade preferida'),
    )
    active = models.BooleanField(
        default=True,
        verbose_name=_('Notificações ativas'),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Preferência de notificação')
        verbose_name_plural = _('Preferências de notificação')

    @property
    def area_list(self) -> list[str]:
        return [a for a in self.area.split(',') if a]

    def __str__(self):
        return f'Preferência de {self.user.email}'
