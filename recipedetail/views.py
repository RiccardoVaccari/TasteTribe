from typing import Any
from uuid import uuid4
from datetime import date, timedelta
from django.views.generic import DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.http import JsonResponse
from django.shortcuts import redirect
from django.views.decorators.http import require_GET

from homepage.models import Recipe, Tag, TagXRecipe
from .models import Ingredient, Allergen, IngredientXRecipe, RecipeStep
from .forms import CreateRecipeForm, EditRecipeForm 


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
        self.recipe_steps: list[RecipeStep] = list()
        self.tags_x_recipe: list[TagXRecipe] = list()

        # Create the Ingreidients
        for ingredient_data in form.cleaned_data.get("ingredients_list"):
            allergens = ingredient_data.get("allergens")
            ingredient_name = ingredient_data.get("name")

            ingredient, tag = create_ingredient(allergens, ingredient_name)
            
            ingredient_x_recipe = IngredientXRecipe(
                ixr_recipe_guid=recipe,
                ixr_ingredient_guid=ingredient,
                ixr_dosage_per_person=ingredient_data.get("dosage")
            )
            self.ingredients_x_recipe.append(ingredient_x_recipe)

            tag_x_recipe = TagXRecipe(
                txr_recipe_guid=recipe,
                txr_tag_guid=tag
            )
            self.tags_x_recipe.append(tag_x_recipe)
        
        # Create the RecipeSteps
        for i, step_data in enumerate(form.cleaned_data.get("steps_list")):
            step = RecipeStep(
                step_sequential_id=i+1,
                step_recipe_guid=recipe,
                step_description=step_data.get("description"),
                step_image="",
                step_required_time=f"{step_data.get("hours")}:{step_data.get("minutes")}"
            )
            self.recipe_steps.append(step)
        
        # Create the tags

        for tag_data in form.cleaned_data.get("tags_list"):
            tag_query = Tag.objects.filter(tag_name__iexact=tag_data)
            if tag_query.exists():
               tag = tag_query.first()
            else:
                tag = Tag(
                    tag_guid=uuid4(),
                    tag_name=tag_data,
                    tag_field="Custom",
                    tag_relevance=5
                )
                tag.save()
            
            tag_x_recipe = TagXRecipe(
                txr_recipe_guid=recipe,
                txr_tag_guid=tag
            )
            self.tags_x_recipe.append(tag_x_recipe)
        
        self.tags_x_recipe.append(
            TagXRecipe(
                txr_recipe_guid=recipe,
                txr_tag_guid=Tag.objects.filter(tag_name__iexact=form.cleaned_data.get("recipe_category")).first()
            )
        )
        
        return super().form_valid(form)
    
    def get_success_url(self) -> str:
        for ixr in self.ingredients_x_recipe:
            ixr.save()

        for step in self.recipe_steps:
            step.save()

        for txr in self.tags_x_recipe:
            txr.save()

        return f"/recipe/{self.object.pk}"


class RecipeEditView(UpdateView):
    model = Recipe
    form_class = EditRecipeForm
    template_name = "recipe_edit.html"
    pk_url_kwarg = "recipe_guid"

    def dispatch(self, request, *args, **kwargs):
        recipe: Recipe = self.get_object()
        if recipe.recipe_author != self.request.user:
            return redirect("recipe_details", recipe_guid=recipe.recipe_guid)
        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        initial = super().get_initial()

        prep_time = self.get_object().recipe_prep_time
        initial['hours'] = prep_time.seconds // 3600
        initial['minutes'] = (prep_time.seconds // 60) % 60

        return initial

    def form_valid(self, form):
        recipe: Recipe = self.get_object()
        
        # INGREDIENTS
        existing_ingredients = set(recipe.ingredientxrecipe_set.values_list('ixr_ingredient_guid__ingredient_name', flat=True))

        new_ingredients_data = form.cleaned_data.get("ingredients_list")
        new_ingredients = set(ingredient_data.get("name") for ingredient_data in new_ingredients_data)

        ingredients_to_remove = existing_ingredients - new_ingredients
        ingredients_to_add = new_ingredients - existing_ingredients

        IngredientXRecipe.objects.filter(ixr_recipe_guid=recipe, ixr_ingredient_guid__ingredient_name__in=ingredients_to_remove).delete()
        TagXRecipe.objects.filter(txr_recipe_guid=recipe, txr_tag_guid__tag_name__in=ingredients_to_remove).delete()

        for ingredient_data in new_ingredients_data:
            allergens = ingredient_data.get("allergens")
            ingredient_name = ingredient_data.get("name")
            if ingredient_name in ingredients_to_add:
                ingredient, tag = create_ingredient(allergens, ingredient_name)

                ingredient_x_recipe = IngredientXRecipe(
                    ixr_recipe_guid=recipe,
                    ixr_ingredient_guid=ingredient,
                    ixr_dosage_per_person=ingredient_data.get("dosage")
                ).save()

                tag_x_recipe = TagXRecipe(
                    txr_recipe_guid=recipe,
                    txr_tag_guid=tag
                ).save()
        
        # STEPS
        new_steps_data = form.cleaned_data.get("steps_list")
        existing_steps = RecipeStep.objects.filter(step_recipe_guid=recipe).order_by('step_sequential_id')

        keep_steps = set()

        for index, step_data in enumerate(new_steps_data):
            step_sequential_id = index + 1
            description = step_data.get("description")
            hours = step_data.get("hours", 0)
            minutes = step_data.get("minutes", 0)
            required_time = timedelta(hours=int(hours), minutes=int(minutes))

            step, created = RecipeStep.objects.update_or_create(
                step_recipe_guid=recipe,
                step_sequential_id=step_sequential_id,
                defaults={
                    "step_description": description,
                    "step_required_time": required_time,
                }
            )
            keep_steps.add(step_sequential_id)

        existing_steps.exclude(step_sequential_id__in=keep_steps).delete()

        return super().form_valid(form)

    def get_success_url(self) -> str:
        return f"/recipe/{self.get_object().pk}"

@require_GET
def check_ingredient(request, *args, **kwargs):
    
    # Ottieni il nome dell'ingrediente dalla query string
    ingredient_name = request.GET.get('ingredient', '').strip()

    # Verifica se l'ingrediente esiste nel database (case insensitive)
    exists = Ingredient.objects.filter(ingredient_name__iexact=ingredient_name).exists()

    return JsonResponse({'exists': exists})

def create_ingredient(allergens: list | None, ingredient_name: str):
    if allergens is None:   # Ingrediente già presente nel db
        ingredient = Ingredient.objects.filter(ingredient_name__iexact=ingredient_name).first()
        tag = Tag.objects.filter(tag_name__iexact=ingredient_name).first()
    else:
        ingredient = Ingredient(
            ingredient_guid=uuid4(),
            ingredient_name=ingredient_name.capitalize(),
            ingredient_allergens=[int(allergen["id"]) for allergen in allergens],
        )
        tag = None
        ingredient.save()

    if not tag:
        tag = Tag(
            tag_guid=uuid4(),
            tag_name=ingredient_name.capitalize(),
            tag_field="Ingredient",
            tag_relevance=10
        )
        tag.save()

    return ingredient, tag