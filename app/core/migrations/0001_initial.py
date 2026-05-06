# Generated manually - Initial migration for SearchRequest model

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='SearchRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('query', models.CharField(max_length=500, verbose_name='Termo de busca')),
                ('area', models.CharField(blank=True, max_length=200, null=True, verbose_name='Área de conhecimento')),
                ('modality', models.CharField(blank=True, max_length=50, null=True, verbose_name='Modalidade')),
                ('state', models.CharField(blank=True, max_length=2, null=True, verbose_name='Estado')),
                ('status', models.CharField(choices=[('pending', 'Pendente'), ('processing', 'Em Andamento'), ('completed', 'Concluída'), ('failed', 'Falhou')], default='pending', max_length=20, verbose_name='Status')),
                ('results_count', models.IntegerField(default=0, verbose_name='Quantidade de resultados')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Criado em')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Atualizado em')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='search_requests', to=settings.AUTH_USER_MODEL, verbose_name='Usuário')),
            ],
            options={
                'verbose_name': 'Requisição de Pesquisa',
                'verbose_name_plural': 'Requisições de Pesquisa',
                'ordering': ['-created_at'],
            },
        ),
    ]
