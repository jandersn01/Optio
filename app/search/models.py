from django.db import models
from .choices import SearchModality, SearchStatus, SearchStates_Br, SearchArea
from django.conf import settings


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

     is_deleted = models.BooleanField(
        default=False,
        verbose_name="Excluído",
     )

     deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Excluído em",
     )

     objects = SearchRequestManager()
     all_objects = models.Manager()

     class Meta:
        verbose_name = "Requisição de busca"
        verbose_name_plural = "Requisições de busca"
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
        verbose_name="Requisição de busca",
    )
    name = models.CharField(max_length=255, verbose_name="Nome do curso")
    institution = models.CharField(max_length=255, verbose_name="Instituição")
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
    link = models.URLField(blank=True, verbose_name="Link")

    class Meta:
        verbose_name = "Curso"
        verbose_name_plural = "Cursos"

    def __str__(self):
        return f"{self.name} — {self.institution}"


class Favorite(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="favorites",
        verbose_name="Usuário",
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="favorited_by",
        verbose_name="Curso",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Adicionado em",
    )

    class Meta:
        verbose_name = "Favorito"
        verbose_name_plural = "Favoritos"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "course"],
                name="unique_user_course_favorite",
            )
        ]

    def __str__(self):
        return f"{self.user.email} - {self.course.name}"