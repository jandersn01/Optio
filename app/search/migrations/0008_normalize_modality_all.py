"""Normaliza modality="all" (sentinela antigo de filtro) para "" (vazio),
agora que "Todas" é tratado só na camada de formulário e não no enum persistido."""
from django.db import migrations


def normalize_modality(apps, schema_editor):
    for model_name in ('SearchRequest', 'SavedAlert', 'Course'):
        model = apps.get_model('search', model_name)
        model.objects.filter(modality='all').update(modality='')


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('search', '0007_remove_savedalert_frequency_alter_course_modality_and_more'),
    ]

    operations = [
        migrations.RunPython(normalize_modality, noop),
    ]
