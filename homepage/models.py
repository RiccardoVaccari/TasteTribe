from django.db import models
from login.models import RegisteredUser


# Create your models here.

class Recipe(models.Model):
    recipe_guid = models.UUIDField(primary_key=True)
    recipe_name = models.CharField(max_length=50)
    recipe_prep_time = models.TimeField()
    recipe_cover = models.TextField()
    recipe_notes = models.CharField(max_length=500)
    recipe_description = models.CharField(max_length=100)
    recipe_category = models.TextField()
    recipe_is_private = models.BooleanField()
    recipe_is_vegetarian = models.BooleanField()
    recipe_gluten_free = models.BooleanField()
    recipe_is_vegan = models.BooleanField()
    recipe_creation_date = models.DateField(default=None)
    recipe_author = models.ForeignKey(RegisteredUser, on_delete=models.PROTECT)


class Tag(models.Model):
    tag_guid = models.UUIDField(primary_key=True)
    tag_name = models.CharField(max_length=100)
    tag_field = models.CharField(max_length=50)
    tag_relevance = models.IntegerField()
