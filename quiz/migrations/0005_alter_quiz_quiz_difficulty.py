# Generated by Django 5.1 on 2024-08-29 09:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0004_quiz_quiz_creation_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quiz',
            name='quiz_difficulty',
            field=models.CharField(choices=[('easy', 'Facile'), ('medium', 'Media'), ('hard', 'Difficile')], max_length=10),
        ),
    ]