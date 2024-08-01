from django import template
from homepage.models import *
from recipedetail.models import *
from homepage.views import check_user_suspension

register = template.Library()


@register.inclusion_tag("recipe_steps.html")
def render_recipe_steps(recipe_guid):
    try:
        steps = RecipeStep.objects.filter(step_recipe_guid=recipe_guid).order_by("step_sequential_id")
        return {"steps": steps}
    except Recipe.DoesNotExist:
        return {"steps": None}


@register.inclusion_tag("recipe_tags.html")
def render_recipe_related_tags(recipe_guid):
    try:
        tags_in_recipe = TagXRecipe.objects.filter(txr_recipe_guid=recipe_guid)
        tags = []
        for tag_x_recipe in tags_in_recipe:
            tag_guid = tag_x_recipe.txr_tag_guid.tag_guid
            tags.append(Tag.objects.get(tag_guid=tag_guid))
        return {"tags": tags}
    except Recipe.DoesNotExist:
        return {"tags": None}


@register.inclusion_tag("recipe_reviews.html")
def render_recipe_reviews(logged_user, recipe_guid):
    try:
        reviews = Review.objects.filter(review_recipe_guid=recipe_guid)
        # Check if the user is suspended
        reg_user = RegisteredUser.objects.get(user=logged_user)
        if check_user_suspension(reg_user):
            locked_reviews = True
        else:
            locked_reviews = False
        return {"reviews": reviews, "locked_reviews": locked_reviews}
    except Recipe.DoesNotExist:
        return {"reviews": None}


@register.inclusion_tag("recipe_ingredient_list.html")
def render_recipe_ingredients(recipe_guid):
    try:
        ingredients_in_recipe = IngredientXRecipe.objects.filter(ixr_recipe_guid=recipe_guid)
        ingredients = []
        for ingredient in ingredients_in_recipe:
            ingredient_guid = ingredient.ixr_ingredient_guid.ingredient_guid
            dosage = ingredient.ixr_dosage_per_person
            allergen_list = Allergen.objects.filter(allergen_id__in=ingredient.ixr_ingredient_guid.ingredient_allergens)
            allergens = []
            for allergen in allergen_list:
                allergens.append(Allergen.objects.get(allergen_id=allergen.allergen_id))
            ingredients.append({
                "ingredient": Ingredient.objects.get(ingredient_guid=ingredient_guid),
                "dosage": dosage,
                "allergens": allergens
            })
        return {"ingredients": ingredients}
    except Recipe.DoesNotExist:
        return {"ingredients": None}
