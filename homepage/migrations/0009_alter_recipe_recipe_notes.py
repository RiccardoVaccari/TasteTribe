# Generated by Django 5.1 on 2024-08-29 09:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('homepage', '0008_alter_recipe_recipe_description_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='recipe_notes',
            field=models.CharField(max_length=500),
        ),
    ]
