# Generated by Django 5.0.7 on 2024-07-27 15:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0002_alter_quiz_quiz_author'),
    ]

    operations = [
        migrations.AddField(
            model_name='quizquestion',
            name='question_text',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
    ]
