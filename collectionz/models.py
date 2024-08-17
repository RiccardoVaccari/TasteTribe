from django.db import models
from homepage.models import Recipe
from login.models import RegisteredUser, User


# Create your models here.

class RecipesCollection(models.Model):
    collection_guid = models.UUIDField(primary_key=True)
    collection_name = models.CharField(max_length=150)
    collection_cover = models.TextField()
    collection_author = models.ForeignKey(User, on_delete=models.PROTECT)
    collection_creation_date = models.DateField()
    collection_is_private = models.BooleanField()


class RecipeXCollection(models.Model):
    rxc_collection_guid = models.ForeignKey(RecipesCollection, on_delete=models.CASCADE)
    rxc_recipe_guid = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    class Meta:
        unique_together = [["rxc_collection_guid", "rxc_recipe_guid"]]
