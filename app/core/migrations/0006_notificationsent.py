import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_rename_policy_acceptad_customuser_policy_accepted'),
    ]

    operations = [
        migrations.CreateModel(
            name='NotificationSent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('course_fingerprint', models.CharField(db_index=True, max_length=64, verbose_name='Fingerprint do curso')),
                ('course_name', models.CharField(max_length=255, verbose_name='Nome do curso')),
                ('course_institution', models.CharField(max_length=255, verbose_name='Instituição')),
                ('course_link', models.URLField(blank=True, verbose_name='Link')),
                ('sent_at', models.DateTimeField(auto_now_add=True, verbose_name='Notificado em')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications_sent', to=settings.AUTH_USER_MODEL, verbose_name='Usuário')),
            ],
            options={
                'verbose_name': 'Notificação enviada',
                'verbose_name_plural': 'Notificações enviadas',
                'ordering': ['-sent_at'],
            },
        ),
        migrations.AddConstraint(
            model_name='notificationsent',
            constraint=models.UniqueConstraint(fields=('user', 'course_fingerprint'), name='unique_user_course_notification'),
        ),
    ]
