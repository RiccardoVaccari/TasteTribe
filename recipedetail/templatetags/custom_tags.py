from django import template
from recipedetail.models import *

register = template.Library()


@register.inclusion_tag("recipedetails/recipe_steps.html")
def render_recipe_steps(recipe_guid):
    try:
        displayed_recipe = Recipe.objects.get(recipe_guid=recipe_guid)
        steps = RecipeStep.objects.filter(step_recipe_guid=recipe_guid).order_by("step_sequential_id")
        return {"steps": steps, "recipe": displayed_recipe}
    except Recipe.DoesNotExist:
        return {"steps": None, "recipe": None}
