# Generated by Django 5.0.7 on 2024-07-17 15:27

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('homepage', '0002_tag_remove_recipe_id_alter_recipe_recipe_guid'),
    ]

    operations = [
        migrations.CreateModel(
            name='Allergen',
            fields=[
                ('allergen_id', models.IntegerField(primary_key=True, serialize=False)),
                ('allergen_name', models.CharField(max_length=100)),
                ('allergen_description', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Ingredient',
            fields=[
                ('ingredient_guid', models.UUIDField(primary_key=True, serialize=False)),
                ('ingredient_name', models.CharField(max_length=100)),
                ('ingredient_image', models.TextField()),
                ('ingredient_category', models.CharField(max_length=100)),
                ('ingredient_allergens', models.JSONField()),
            ],
        ),
        migrations.CreateModel(
            name='IngredientXRecipe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ixr_dosage_per_person', models.CharField(max_length=50)),
                ('ixr_ingredient_guid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recipedetail.ingredient')),
                ('ixr_recipe_guid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='homepage.recipe')),
            ],
            options={
                'unique_together': {('ixr_recipe_guid', 'ixr_ingredient_guid')},
            },
        ),
        migrations.CreateModel(
            name='RecipeStep',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('step_sequential_id', models.IntegerField()),
                ('step_description', models.TextField()),
                ('step_image', models.TextField()),
                ('step_required_time', models.TimeField()),
                ('step_recipe_guid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='homepage.recipe')),
            ],
            options={
                'unique_together': {('step_sequential_id', 'step_recipe_guid')},
            },
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('review_grade', models.IntegerField()),
                ('review_notes', models.TextField()),
                ('review_up_votes', models.IntegerField()),
                ('review_down_votes', models.IntegerField()),
                ('review_author_guid', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='login.registereduser')),
                ('review_recipe_guid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='homepage.recipe')),
            ],
            options={
                'unique_together': {('review_recipe_guid', 'review_author_guid')},
            },
        ),
    ]
