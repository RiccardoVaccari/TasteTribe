# Generated by Django 5.0.7 on 2024-08-01 18:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0004_alter_forummessageinteraction_unique_together'),
    ]

    operations = [
        migrations.AlterField(
            model_name='forummessageinteraction',
            name='interaction_liked',
            field=models.IntegerField(null=True),
        ),
    ]