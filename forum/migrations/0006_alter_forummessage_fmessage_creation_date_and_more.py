# Generated by Django 5.0.7 on 2024-08-01 19:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0005_alter_forummessageinteraction_interaction_liked'),
    ]

    operations = [
        migrations.AlterField(
            model_name='forummessage',
            name='fmessage_creation_date',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='forumthread',
            name='fthread_creation_date',
            field=models.DateTimeField(),
        ),
    ]