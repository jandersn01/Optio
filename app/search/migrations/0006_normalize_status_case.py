"""Normaliza valores de status gravados em MAIÚSCULO (regressão do refactor do
worker) para os valores minúsculos definidos em SearchStatus."""
from django.db import migrations

STATUS_MAP = {
    'PENDING': 'pending',
    'PROCESSING': 'processing',
    'COMPLETED': 'completed',
    'FAILED': 'failed',
    'NO_RESULTS': 'no_results',
}


def normalize_status(apps, schema_editor):
    SearchRequest = apps.get_model('search', 'SearchRequest')
    for old_value, new_value in STATUS_MAP.items():
        SearchRequest.objects.filter(status=old_value).update(status=new_value)


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('search', '0005_savedalert'),
    ]

    operations = [
        migrations.RunPython(normalize_status, noop),
    ]
