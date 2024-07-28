from typing import Any
from uuid import uuid4
from datetime import date
from django.views.generic import DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404

from .models import Ingredient, Recipe, Allergen, IngredientXRecipe
from .forms import CreateRecipeForm


# RECIPE DETAILS APP - VIEWS
class RecipeDetailView(DetailView):
    model = Recipe
    template_name = "recipe_details.html"
    context_object_name = "recipe"
    pk_url_kwarg = "recipe_guid"

    def get_object(self, queryset=None):
        guid_string = self.kwargs.get(self.pk_url_kwarg)
        try:
            # guid_obj = UUID(guid_string)
            return Recipe.objects.get(recipe_guid=guid_string)
        except ValueError:
            raise Http404("Invalid GUID format passed in the url")
        except Recipe.DoesNotExist:
            raise Http404("No recipe found matching the query")


class RecipeCreateView(LoginRequiredMixin, CreateView):
    model = Recipe
    form_class = CreateRecipeForm
    template_name = "recipe_create.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['allergens'] = Allergen.objects.all().values("allergen_id", "allergen_name", "allergen_description")
        return context

    def form_valid(self, form):
        
        # Set the Recipe attributes
        recipe: Recipe = form.instance
        recipe.recipe_guid = uuid4()
        recipe.recipe_prep_time = f"{form.cleaned_data.get("hours")}:{form.cleaned_data.get("minutes")}"
        recipe.recipe_author = self.request.user
        recipe.recipe_creation_date = date.today()
        form.instance = recipe

        self.ingredients_x_recipe: list[IngredientXRecipe] = list()
        # Create the Ingreidients and the Allergen
        for ingredient_data in form.cleaned_data.get("ingredients_list"):
            allergens = ingredient_data.get("allergens")

            if allergens is None:   # Ingrediente già presente nel db
                ingredient = Ingredient.objects.filter(ingredient_name__iexact=ingredient_data.get("name")).first()
            else:
                ingredient = Ingredient(
                    ingredient_guid=uuid4(),
                    ingredient_name=ingredient_data.get("name"),
                    ingredient_allergens=[int(allergen["id"]) for allergen in ingredient_data.get("allergens")],
                )
                ingredient.save()
            
            ingredient_x_recipe = IngredientXRecipe(
                ixr_recipe_guid=recipe,
                ixr_ingredient_guid=ingredient,
                ixr_dosage_per_person=ingredient_data.get("dosage")
            )
            self.ingredients_x_recipe.append(ingredient_x_recipe)

        return super().form_valid(form)
    
    def get_success_url(self) -> str:
        for ixr in self.ingredients_x_recipe:
            ixr.save()

        return f"/recipe/{self.object.pk}"


from django.http import JsonResponse
from django.views.decorators.http import require_GET

# @require_GET
# def get_allergens(request):
#     allergens = Allergen.objects.all().values("allergen_id", "allergen_name", "allergen_description")
#     return JsonResponse(list(allergens), safe=False)

@require_GET
def check_ingredient(request, *args, **kwargs):
    
    # Ottieni il nome dell'ingrediente dalla query string
    ingredient_name = request.GET.get('ingredient', '').strip()

    # Verifica se l'ingrediente esiste nel database (case insensitive)
    exists = Ingredient.objects.filter(ingredient_name__iexact=ingredient_name).exists()

    return JsonResponse({'exists': exists})
