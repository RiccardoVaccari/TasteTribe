from typing import Any
from uuid import uuid4
from datetime import date
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
from django.views.generic.edit import FormMixin
from collectionz.forms import CollectionCreationForm
from collectionz.views import collection_creation
from homepage.models import *
from collectionz.models import *
from .models import *
from forum.views import elaborate_interaction
from .forms import CreateRecipeForm


# RECIPE DETAILS APP - VIEWS
class RecipeDetailView(FormMixin, DetailView):
    model = Recipe
    template_name = "recipe_details.html"
    context_object_name = "recipe"
    pk_url_kwarg = "recipe_guid"
    form_class = CollectionCreationForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get the logged user
        user = self.request.user
        # Get the recipe to be displayed
        context["recipe"] = self.get_object()
        context["user"] = user
        # If the user is registered then handle the possibility to add the recipe to a collection
        if user.is_authenticated:
            context["user_collections"] = RecipesCollection.objects.filter(collection_author=user.id)
        return context

    def get_object(self, queryset=None):
        guid_string = self.kwargs.get(self.pk_url_kwarg)
        try:
            # guid_obj = UUID(guid_string)
            return Recipe.objects.get(recipe_guid=guid_string)
        except ValueError:
            raise Http404("Invalid GUID format passed in the url")
        except Recipe.DoesNotExist:
            raise Http404("No recipe found matching the query")

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            collection = form.save(commit=False)
            collection_creation(collection, request)
            # After creating the collection, we now need to insert the current recipe into the collection
            recipe_x_collection = RecipeXCollection.objects.create(rxc_recipe_guid=self.get_object(), rxc_collection_guid=collection)
            recipe_x_collection.save()  # This line might not be needed
            return JsonResponse({"success": True})
        else:
            return self.form_invalid(form)


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

            if allergens is None:   # Ingrediente già presente nel db
                ingredient = Ingredient.objects.filter(ingredient_name__iexact=ingredient_name).first()
                tag = Tag.objects.filter(tag_name__iexact=tag_data).first()
            else:
                ingredient = Ingredient(
                    ingredient_guid=uuid4(),
                    ingredient_name=ingredient_name.capitalize(),
                    ingredient_allergens=[int(allergen["id"]) for allergen in allergens],
                )
                tag = Tag(
                    tag_guid=uuid4(),
                    tag_name=ingredient_name.capitalize(),
                    tag_field="Ingredient",
                    tag_relevance=10
                )
                ingredient.save()
                tag.save()
            
            ingredient_x_recipe = IngredientXRecipe(
                ixr_recipe_guid=recipe,
                ixr_ingredient_guid=ingredient,
                ixr_dosage_per_person=ingredient_data.get("dosage")[:50]
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


@require_GET
def check_ingredient(request, *args, **kwargs):
    
    # Ottieni il nome dell'ingrediente dalla query string
    ingredient_name = request.GET.get('ingredient', '').strip()

    # Verifica se l'ingrediente esiste nel database (case insensitive)
    exists = Ingredient.objects.filter(ingredient_name__iexact=ingredient_name).exists()

    return JsonResponse({'exists': exists})


@login_required
@require_POST
def toggle_review_interaction(request):
    # Fetch the review and the user data
    review_id = request.POST.get("review_id")
    interaction_type = request.POST.get("interaction_type")
    user = request.user
    review = get_object_or_404(Review, id=review_id)
    interaction, created = ReviewInteraction.objects.get_or_create(rev_interaction_review=review, rev_interaction_user=user)
    user_rev_interaction = elaborate_interaction(interaction, created, interaction_type)
    review.review_up_votes = ReviewInteraction.objects.filter(rev_interaction_review=review, interaction_liked=REVIEW_INTERACTION_LIKE).count()
    review.review_down_votes = ReviewInteraction.objects.filter(rev_interaction_review=review, interaction_liked=REVIEW_INTERACTION_DISLIKE).count()
    review.save()
    return JsonResponse({
        "review_id": review_id,
        "review_notes": review.review_notes,
        "review_author": f"{review.review_author_guid.first_name} {review.review_author_guid.last_name}",
        "likes": review.review_up_votes,
        "dislikes": review.review_down_votes,
        "review_grade": review.review_grade,
        "user_rev_interaction": user_rev_interaction
    })


@require_POST
def add_to_collection(request):
    # Fetch parameters passed by frontend
    collection_guid = request.POST.get("collection_guid")
    recipe_guid = request.POST.get("recipe_guid")
    # Obtain respective objects from the database
    collection = RecipesCollection.objects.get(collection_guid=collection_guid)
    recipe = Recipe.objects.get(recipe_guid=recipe_guid)
    # Create the bound between the two objects
    recipe_x_collection = RecipeXCollection.objects.create(rxc_collection_guid=collection, rxc_recipe_guid=recipe)
    recipe_x_collection.save()
    # Send the response to the frontend
    response_data = {
        "status": "success",
        "message": f"La ricetta {recipe.recipe_name} è stata aggiunta con successo nella raccolta {collection.collection_name}"
    }
    return JsonResponse(response_data)
