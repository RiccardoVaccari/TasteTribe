from typing import Any
from uuid import uuid4
from datetime import date, timedelta
from random import choice
from django.views.generic import DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_GET, require_POST
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.db.models import Count, Q
from django.contrib import messages


from homepage.models import Recipe, Tag, TagXRecipe
from .models import *
from forum.views import elaborate_interaction
from login.models import RegisteredUser
from utils import check_user_suspension
from .forms import CreateRecipeForm, EditRecipeForm, ReviewForm


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

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        recipe: Recipe = self.get_object()

        try:
            reg_user = RegisteredUser.objects.get(user=self.request.user.id)
            user_suspended = check_user_suspension(reg_user)
            if user_suspended:
                return super().get_context_data(**kwargs)

        except RegisteredUser.DoesNotExist:
            return super().get_context_data(**kwargs)

        if recipe.recipe_author != self.request.user:
            context["owner"] = False

            # Update tags history
            tags_query = Tag.objects.filter(
                tagxrecipe__txr_recipe_guid__recipe_guid=recipe.recipe_guid).values_list('tag_name', flat=True)
            reg_user.reg_user_search_history["tags"] = list(
                set(list(tags_query) + reg_user.reg_user_search_history["tags"]))[:30]

            # Update recipes history
            recipes_history = reg_user.reg_user_search_history["recipes"]
            recipes_history.insert(0, str(recipe.recipe_guid))
            reg_user.reg_user_search_history["recipes"] = list(set(recipes_history))[
                :10]
            reg_user.save()

        else:
            context["owner"] = True

        context["related_recipes"] = list()

        # Aggiungi ricette dello stesso autore
        author_related_recipes = Recipe.objects.filter(
            recipe_author=recipe.recipe_author
        ).exclude(
            Q(recipe_guid=recipe.recipe_guid) |
            Q(recipe_is_private=True)
        )
        if author_related_recipes.exists():
            context["related_recipes"].append(
                choice(list(author_related_recipes)))

        # Trova il tag "Course" associato alla ricetta corrente
        portata_tag = Tag.objects.filter(
            tagxrecipe__txr_recipe_guid=recipe,
            tag_field="Course"
        ).first()

        # Filtra le ricette che hanno lo stesso tag "Course"
        if portata_tag:
            related_recipes = Recipe.objects.filter(
                tagxrecipe__txr_tag_guid=portata_tag
            ).exclude(
                Q(recipe_guid=recipe.recipe_guid) | 
                Q(recipe_is_private=True) | 
                Q(recipe_author=self.request.user)
            )

            if related_recipes.exists():
                context["related_recipes"].append(
                    choice(list(related_recipes)))

        user_recent_tags = reg_user.reg_user_search_history.get("tags", [])

        if user_recent_tags:
            recommended_recipes = Recipe.objects.filter(
                tagxrecipe__txr_tag_guid__tag_name__in=user_recent_tags
            ).exclude(
                Q(recipe_guid=recipe.recipe_guid) |
                Q(recipe_is_private=True) |
                Q(recipe_author=self.request.user)
            ).annotate(
                matched_tags=Count('tagxrecipe__txr_tag_guid')
            ).order_by('-matched_tags')

            if recommended_recipes.exists():
                context["related_recipes"].extend(list(recommended_recipes))

        context["related_recipes"] = context["related_recipes"][:3]

        return context


class RecipeCreateView(LoginRequiredMixin, CreateView):
    model = Recipe
    form_class = CreateRecipeForm
    template_name = "recipe_create.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['allergens'] = Allergen.objects.all().values(
            "allergen_id", "allergen_name", "allergen_description")
        return context

    def form_valid(self, form):

        # Set the Recipe attributes
        recipe: Recipe = form.instance
        recipe.recipe_guid = uuid4()
        recipe.recipe_prep_time = f"{form.cleaned_data.get(
            "hours")}:{form.cleaned_data.get("minutes")}"
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
                step_required_time=f"{step_data.get("hours")}:{
                    step_data.get("minutes")}"
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
                txr_tag_guid=Tag.objects.filter(
                    tag_name__iexact=form.cleaned_data.get("recipe_category")).first()
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
        existing_ingredients = set(recipe.ingredientxrecipe_set.values_list(
            'ixr_ingredient_guid__ingredient_name', flat=True))

        new_ingredients_data = form.cleaned_data.get("ingredients_list")
        new_ingredients = set(ingredient_data.get("name")
                              for ingredient_data in new_ingredients_data)

        ingredients_to_remove = existing_ingredients - new_ingredients
        ingredients_to_add = new_ingredients - existing_ingredients

        IngredientXRecipe.objects.filter(
            ixr_recipe_guid=recipe, ixr_ingredient_guid__ingredient_name__in=ingredients_to_remove).delete()
        TagXRecipe.objects.filter(
            txr_recipe_guid=recipe, txr_tag_guid__tag_name__in=ingredients_to_remove).delete()

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
        existing_steps = RecipeStep.objects.filter(
            step_recipe_guid=recipe).order_by('step_sequential_id')

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

        # TAGS

        existing_tags = set(recipe.tagxrecipe_set.exclude(
            txr_tag_guid__tag_field="Ingredient").values_list('txr_tag_guid__tag_name', flat=True))
        new_tags = set(form.cleaned_data.get("tags_list"))

        tags_to_remove = existing_tags - new_tags
        tags_to_add = new_tags - existing_tags

        # Rimuovi i tag che non sono più presenti
        TagXRecipe.objects.filter(
            txr_recipe_guid=recipe, txr_tag_guid__tag_name__in=tags_to_remove).delete()

        # Aggiungi i nuovi tag
        for tag_name in tags_to_add:
            tag, created = Tag.objects.get_or_create(tag_name=tag_name)
            TagXRecipe.objects.create(txr_recipe_guid=recipe, txr_tag_guid=tag)

        return super().form_valid(form)

    def get_success_url(self) -> str:
        return f"/recipe/{self.get_object().pk}"


@require_GET
def check_ingredient(request, *args, **kwargs):

    # Ottieni il nome dell'ingrediente dalla query string
    ingredient_name = request.GET.get('ingredient', '').strip()

    # Verifica se l'ingrediente esiste nel database (case insensitive)
    exists = Ingredient.objects.filter(
        ingredient_name__iexact=ingredient_name).exists()

    return JsonResponse({'exists': exists})


def create_ingredient(allergens: list | None, ingredient_name: str):
    if allergens is None:   # Ingrediente già presente nel db
        ingredient = Ingredient.objects.filter(
            ingredient_name__iexact=ingredient_name).first()
        tag = Tag.objects.filter(tag_name__iexact=ingredient_name).first()
    else:
        ingredient = Ingredient(
            ingredient_guid=uuid4(),
            ingredient_name=ingredient_name.capitalize(),
            ingredient_allergens=[int(allergen["id"])
                                  for allergen in allergens],
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


@login_required
@require_POST
def toggle_review_interaction(request):
    # Fetch the review and the user data
    review_id = request.POST.get("review_id")
    interaction_type = request.POST.get("interaction_type")
    user = request.user
    review = get_object_or_404(Review, id=review_id)
    interaction, created = ReviewInteraction.objects.get_or_create(
        rev_interaction_review=review, rev_interaction_user=user)
    user_rev_interaction = elaborate_interaction(
        interaction, created, interaction_type)
    review.review_up_votes = ReviewInteraction.objects.filter(
        rev_interaction_review=review, interaction_liked=REVIEW_INTERACTION_LIKE).count()
    review.review_down_votes = ReviewInteraction.objects.filter(
        rev_interaction_review=review, interaction_liked=REVIEW_INTERACTION_DISLIKE).count()
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

def delete_recipe(request, recipe_guid):
    if request.method == "POST":
        recipe = get_object_or_404(Recipe, recipe_guid=recipe_guid)
        if recipe.recipe_author == request.user:
            recipe.delete()
            return JsonResponse({"success": True})
        else:
            return JsonResponse({"success": False}, status=403)

    return JsonResponse({"success": False}, status=405)


@login_required
def add_review(request, recipe_guid):
    recipe = get_object_or_404(Recipe, recipe_guid=recipe_guid)
    
    if request.method == 'POST':
        review_grade = request.POST.get('review_grade')
        review_notes = request.POST.get('review_notes')

        # Check if a star rating has been selected
        if not review_grade:
            messages.error(request, 'Devi selezionare un numero di stelle per lasciare una recensione.')
            return redirect('recipe_detail', recipe_guid=recipe.recipe_guid)

        # Check if notes are provided
        if not review_notes:
            messages.error(request, 'Le note della recensione non possono essere vuote.')
            return redirect('recipe_detail', recipe_guid=recipe.recipe_guid)
        
        # Check if user has already reviewed this recipe
        review = Review.objects.filter(review_recipe_guid=recipe, review_author_guid=request.user).first()
        if review:
            # You can either update the existing review or return an error message
            review.review_grade = review_grade
            review.review_notes = review_notes
            review.save()
            response_data = {"new": False}
        else:
            # Create a new review
            review = Review(
                review_recipe_guid=recipe,
                review_author_guid=request.user,
                review_grade=review_grade,
                review_notes=review_notes,
                review_up_votes=0,
                review_down_votes=0
            )
            review.save()
            response_data = {"new": True}
        
        response_data.update({
            "review_id": review.id,
            "author": review.review_author_guid.get_full_name(),
            "review_grade": review.review_grade,
            "review_notes": review.review_notes,
            "review_up_votes": review.review_up_votes,
            "review_down_votes": review.review_down_votes,
        })

        return JsonResponse(response_data)
        
    return redirect("recipe_details", recipe_guid=recipe.recipe_guid)