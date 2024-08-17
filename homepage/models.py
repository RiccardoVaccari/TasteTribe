from django.db import models
from login.models import RegisteredUser, User


# Create your models here.

class Recipe(models.Model):
    recipe_guid = models.UUIDField(primary_key=True)
    recipe_name = models.CharField(max_length=50)
    recipe_prep_time = models.DurationField()
    recipe_cover = models.TextField(null=True)
    recipe_notes = models.CharField(max_length=500)
    recipe_description = models.TextField()
    recipe_category = models.TextField()
    recipe_is_private = models.BooleanField()
    recipe_is_vegetarian = models.BooleanField()
    recipe_gluten_free = models.BooleanField()
    recipe_is_vegan = models.BooleanField()
    recipe_creation_date = models.DateField(default=None)
    recipe_author = models.ForeignKey(User, on_delete=models.PROTECT, null=True)

    def __str__(self) -> str:
        return f"<b>{self.recipe_name.capitalize()}</b> by "

class Tag(models.Model):
    tag_guid = models.UUIDField(primary_key=True)
    tag_name = models.CharField(max_length=100, unique=True)
    tag_field = models.CharField(max_length=50)
    tag_relevance = models.IntegerField()


class TagXRecipe(models.Model):
    txr_recipe_guid = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    txr_tag_guid = models.ForeignKey(Tag, on_delete=models.CASCADE)

    class Meta:
        unique_together = [["txr_recipe_guid", "txr_tag_guid"]]
