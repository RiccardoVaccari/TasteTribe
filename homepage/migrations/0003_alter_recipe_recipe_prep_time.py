# Generated by Django 5.0.7 on 2024-07-24 09:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('homepage', '0002_tag_remove_recipe_id_alter_recipe_recipe_guid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='recipe_prep_time',
            field=models.DurationField(),
        ),
    ]
