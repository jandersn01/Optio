from django.db import migrations

PREMIUM_GROUP = 'Premium'


def create_premium_group(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.get_or_create(name=PREMIUM_GROUP)


def remove_premium_group(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.filter(name=PREMIUM_GROUP).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_notificationsent'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.RunPython(create_premium_group, remove_premium_group),
    ]
