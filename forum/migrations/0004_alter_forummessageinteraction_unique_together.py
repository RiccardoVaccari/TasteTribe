# Generated by Django 5.0.7 on 2024-08-01 16:52

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0003_forummessage_fmessage_content_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='forummessageinteraction',
            unique_together={('interaction_fmessage', 'interaction_user')},
        ),
    ]
