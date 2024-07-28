# Generated by Django 5.0.7 on 2024-07-17 15:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('login', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='registereduser',
            name='id',
        ),
        migrations.AlterField(
            model_name='registereduser',
            name='reg_user_guid',
            field=models.UUIDField(primary_key=True, serialize=False),
        ),
    ]