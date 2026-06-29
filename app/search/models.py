from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .choices import SearchModality, SearchStatus, SearchStates_Br, SearchArea


class SearchRequestQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_deleted=False)

    def for_user(self, user):
        return self.filter(user=user)


class SearchRequestManager(models.Manager):
    def get_queryset(self):
        return SearchRequestQuerySet(self.model, using=self._db).active()

    def for_user(self, user):
        return self.get_queryset().for_user(user)


class SearchRequest(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="search_requests",
        verbose_name=_("Usuário"),
    )

    notification_email = models.EmailField(
        verbose_name=_("E-mail para notificação"),
    )

    keywords = models.CharField(
        max_length=255,
        verbose_name=_("Palavras-chave"),
    )

    area = models.CharField(
        max_length=100,
        choices=SearchArea.choices,
        blank=True,
        verbose_name=_("Área do conhecimento"),
    )

    modality = models.CharField(
        max_length=20,
        choices=SearchModality.choices,
        blank=True,
        verbose_name=_("Modalidade"),
    )

    state = models.CharField(
        max_length=2,
        choices=SearchStates_Br.choices,
        blank=True,
        verbose_name=_("Estado"),
    )

    status = models.CharField(
        max_length=20,
        choices=SearchStatus.choices,
        default=SearchStatus.PENDING,
        verbose_name=_("Status"),
    )

    results_count = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Quantidade de resultados"),
    )

    is_deleted = models.BooleanField(
        default=False,
        verbose_name=_("Excluído"),
    )

    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Excluído em"),
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Criado em"),
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Atualizado em"),
    )

    objects = SearchRequestManager()
    all_objects = models.Manager()

    class Meta:
        verbose_name = _("Requisição de busca")
        verbose_name_plural = _("Requisições de busca")
        ordering = ["-created_at"]
        default_manager_name = "objects"

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
        }
        return colors.get(self.status, "secondary")

    @property
    def relative_time(self) -> str:
        diff = timezone.now() - self.created_at
        s = diff.total_seconds()
        if s < 60:
            return "agora mesmo"
        if s < 3600:
            m = int(s // 60)
            return f"há {m} min"
        if s < 86400:
            h = int(s // 3600)
            return f"há {h}h"
        if s < 86400 * 2:
            return "ontem"
        if s < 86400 * 7:
            return f"há {int(s // 86400)} dias"
        return self.created_at.strftime("%d/%m/%Y")

    @property
    def status_icon(self):
        icons = {
            "pending": "⏳",
            "processing": "🔄",
            "completed": "✅",
            "failed": "❌",
            "no_results": "🔍",
        }
        return icons.get(self.status, "•")


class Course(models.Model):
    search_request = models.ForeignKey(
        SearchRequest,
        on_delete=models.CASCADE,
        related_name="courses",
        verbose_name=_("Requisição de busca"),
    )
    name = models.CharField(max_length=255, verbose_name=_("Nome do curso"))
    institution = models.CharField(max_length=255, verbose_name=_("Instituição"))
    modality = models.CharField(
        max_length=20,
        choices=SearchModality.choices,
        blank=True,
        verbose_name=_("Modalidade"),
    )
    state = models.CharField(
        max_length=2,
        choices=SearchStates_Br.choices,
        blank=True,
        verbose_name=_("Estado"),
    )
    link = models.URLField(blank=True, verbose_name=_("Link"))

    class Meta:
        verbose_name = _("Curso")
        verbose_name_plural = _("Cursos")

    def __str__(self):
        return f"{self.name} — {self.institution}"


class Favorite(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="favorites",
        verbose_name=_("Usuário"),
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="favorited_by",
        verbose_name=_("Curso"),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Adicionado em"),
    )

    class Meta:
        verbose_name = _("Favorito")
        verbose_name_plural = _("Favoritos")
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "course"],
                name="unique_user_course_favorite",
            )
        ]

    def __str__(self):
        return f"{self.user.email} — {self.course.name}"


class SavedAlert(models.Model):
    """Uma busca que o usuário salvou como alerta. O job de notificação verifica
    periodicamente, por usuário, se surgiram cursos novos aderentes aos critérios."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="saved_alerts",
        verbose_name="Usuário",
    )
    name = models.CharField(max_length=120, verbose_name="Nome do alerta")
    keywords = models.CharField(max_length=255, verbose_name="Palavras-chave")
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
    active = models.BooleanField(default=True, verbose_name="Ativo")
    last_checked_at = models.DateTimeField(
        null=True, blank=True, verbose_name="Última verificação"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    class Meta:
        verbose_name = "Alerta salvo"
        verbose_name_plural = "Alertas salvos"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Alerta de {self.user.email}: {self.name}"
