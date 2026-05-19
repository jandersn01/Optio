import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("search", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Course",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=255, verbose_name="Nome do curso")),
                ("institution", models.CharField(max_length=255, verbose_name="Instituição")),
                (
                    "modality",
                    models.CharField(
                        blank=True,
                        choices=[("ead", "EAD"), ("presencial", "Presencial"), ("hibrido", "Híbrido"), ("all", "Todos")],
                        max_length=20,
                        verbose_name="Modalidade",
                    ),
                ),
                (
                    "state",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("AC", "Acre"), ("AL", "Alagoas"), ("AP", "Amapá"), ("AM", "Amazonas"),
                            ("BA", "Bahia"), ("CE", "Ceará"), ("DF", "Distrito Federal"), ("ES", "Espírito Santo"),
                            ("GO", "Goiás"), ("MA", "Maranhão"), ("MT", "Mato Grosso"), ("MS", "Mato Grosso do Sul"),
                            ("MG", "Minas Gerais"), ("PA", "Pará"), ("PB", "Paraíba"), ("PR", "Paraná"),
                            ("PE", "Pernambuco"), ("PI", "Piauí"), ("RJ", "Rio de Janeiro"), ("RN", "Rio Grande do Norte"),
                            ("RS", "Rio Grande do Sul"), ("RO", "Rondônia"), ("RR", "Roraima"), ("SC", "Santa Catarina"),
                            ("SP", "São Paulo"), ("SE", "Sergipe"), ("TO", "Tocantins"),
                        ],
                        max_length=2,
                        verbose_name="Estado",
                    ),
                ),
                ("link", models.URLField(blank=True, verbose_name="Link")),
                (
                    "search_request",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="courses",
                        to="search.searchrequest",
                        verbose_name="Requisição de busca",
                    ),
                ),
            ],
            options={
                "verbose_name": "Curso",
                "verbose_name_plural": "Cursos",
            },
        ),
    ]