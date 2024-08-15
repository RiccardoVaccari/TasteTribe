from django.db import models
from homepage.models import Recipe
from login.models import RegisteredUser, User


# Create your models here.
REVIEW_INTERACTION_LIKE = 1
REVIEW_INTERACTION_DISLIKE = -1


class RecipeStep(models.Model):
    step_sequential_id = models.IntegerField()
    step_recipe_guid = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    step_description = models.TextField()
    step_image = models.TextField()
    step_required_time = models.DurationField()

    class Meta:
        unique_together = [["step_sequential_id", "step_recipe_guid"]]


class Ingredient(models.Model):
    ingredient_guid = models.UUIDField(primary_key=True)
    ingredient_name = models.CharField(max_length=100, unique=True)
    ingredient_image = models.TextField()
    ingredient_allergens = models.JSONField()


class IngredientXRecipe(models.Model):
    ixr_recipe_guid = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ixr_ingredient_guid = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    ixr_dosage_per_person = models.CharField(max_length=50)

    class Meta:
        unique_together = [["ixr_recipe_guid", "ixr_ingredient_guid"]]


class Allergen(models.Model):
    allergen_id = models.IntegerField(primary_key=True)
    allergen_name = models.CharField(max_length=100)
    allergen_description = models.CharField(max_length=200)


class Review(models.Model):
    review_recipe_guid = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    review_author_guid = models.ForeignKey(User, on_delete=models.PROTECT, null=True)
    review_grade = models.IntegerField()
    review_notes = models.TextField()
    review_up_votes = models.IntegerField()
    review_down_votes = models.IntegerField()

    class Meta:
        unique_together = [["review_recipe_guid", "review_author_guid"]]


class ReviewInteraction(models.Model):
    rev_interaction_review = models.ForeignKey(Review, on_delete=models.CASCADE)
    rev_interaction_user = models.ForeignKey(User, on_delete=models.CASCADE)
    interaction_liked = models.IntegerField(null=True)

    class Meta:
        unique_together = ("rev_interaction_review", "rev_interaction_user")
