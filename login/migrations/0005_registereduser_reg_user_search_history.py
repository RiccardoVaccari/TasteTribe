# Generated by Django 5.0.7 on 2024-08-01 08:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('login', '0004_alter_registereduser_reg_user_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='registereduser',
            name='reg_user_search_history',
            field=models.JSONField(default={'ingredients': [], 'recipes': [], 'tags': []}),
        ),
    ]