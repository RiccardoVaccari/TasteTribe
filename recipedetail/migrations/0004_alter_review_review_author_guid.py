# Generated by Django 5.0.7 on 2024-07-25 08:54

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('login', '0003_remove_registereduser_reg_user_email_and_more'),
        ('recipedetail', '0003_alter_review_review_author_guid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='review_author_guid',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='login.registereduser'),
        ),
    ]