from datetime import date
from typing import Any

from django.db.models.functions import Random
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.generic import ListView, View
from django.db.models import Q, Count
import thefuzz.fuzz

from recipedetail.models import Ingredient
from login.models import RegisteredUser
from .forms import SearchForm
from .models import *
from common.utils import *


class HomepageView(ListView):
    model = Recipe
    template_name = 'homepage.html'
    context_object_name = 'recipes'
    form = SearchForm()

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            try:
                _ = RegisteredUser.objects.get(user=request.user)
            except RegisteredUser.DoesNotExist:
                return redirect(reverse('edit_profile'))
        
        self.update_notifications()
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        if self.request.user and self.request.user.is_authenticated and not self.user_suspended:
            queryset = Recipe.objects.filter(recipe_is_private=False).exclude(recipe_author=self.request.user)
        else:
            queryset = Recipe.objects.filter(recipe_is_private=False)

        return queryset.order_by(Random())[:200]
    
    def get_form(self):
        return SearchForm(user=self.request.user, user_suspended=self.user_suspended, from_homepage=True)
    
    def update_notifications(self):
        self.notifications_to_read = []
        try:
            reg_user = RegisteredUser.objects.get(user=self.request.user.id)
            self.notifications_to_read = reg_user.reg_user_status.get("notifications", [])
            reg_user.reg_user_status["notifications"] = [] 
            reg_user.save()
            self.user_suspended = check_user_suspension(reg_user)
        except RegisteredUser.DoesNotExist:
            self.user_suspended = False

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['notifications_to_read'] = self.notifications_to_read
        context['form'] = self.get_form()
        context['user'] = self.request.user
        if self.request.user.is_authenticated:
            context["reg_user"] = RegisteredUser.objects.get(user=self.request.user.id)
        # Define a list for the different sections of the homepage
        context["recipes_sections"] = []

        # RS
        if self.request.user and self.request.user.is_authenticated and not self.user_suspended:
            # Latest publications
            latest_recipes = self.get_latest_publish()
            context["recipes_sections"].append({
                "section_title": "Ultime ricette pubblicate",
                "recipe_list": latest_recipes
            })
            # TAGs
            user_recent_tags = RegisteredUser.objects.get(user=self.request.user).reg_user_search_history.get("tags", [])
            if user_recent_tags:
                tags_recipes = self.get_reccomended_by_tags(user_recent_tags)
                context["recipes_sections"].append({
                    "section_title": "In base ai tuoi gusti",
                    "recipe_list": tags_recipes
                })
            # Ingredients
            latest_ingredient = RegisteredUser.objects.get(user=self.request.user).reg_user_search_history.get(
                "ingredients")
            if latest_ingredient:
                ingredient_recipes = self.get_recipes_by_ingredient(latest_ingredient)
                context["recipes_sections"].append({
                    "section_title": f"Altre ricette con {latest_ingredient}",
                    "recipe_list": ingredient_recipes
                })
            # Season
            season = self.__get_season_()
            season_recipes = self.get_recipes_by_season(season)
            context["recipes_sections"].append({
                "section_title": f"Altre ricette in {season}",
                "recipe_list": season_recipes
            })
        return context

    def get_latest_publish(self, n: int = 20):
        return Recipe.objects.exclude(
            Q(recipe_is_private=True) |
            Q(recipe_author=self.request.user)
        ).order_by('-recipe_creation_date')[:int(n)]

    def get_reccomended_by_tags(self, user_recent_tags: list[str], n: int = 20):
        recommended_recipes = Recipe.objects.filter(
            tagxrecipe__txr_tag_guid__tag_name__in=user_recent_tags
        ).exclude(
            Q(recipe_is_private=True) |
            Q(recipe_author=self.request.user)
        ).annotate(
            matched_tags=Count('tagxrecipe__txr_tag_guid')
        ).order_by('-matched_tags')

        if recommended_recipes.exists():
            return list(recommended_recipes)[:n]
        return []

    def get_recipes_by_ingredient(self, ingredient_name: str, n: int = 20):
        try:
            ingredient = Ingredient.objects.get(ingredient_name=ingredient_name)
        except Ingredient.DoesNotExist:
            return Recipe.objects.none()
        recipes = Recipe.objects.filter(
            recipe_is_private=False,
            ingredientxrecipe__ixr_ingredient_guid=ingredient,
        ).exclude(recipe_author=self.request.user).distinct()
        return recipes[:int(n)]

    def get_recipes_by_season(self, current_season: str, n: int = 20):
        if current_season:
            recipes = Recipe.objects.filter(
                recipe_is_private=False,
                tagxrecipe__txr_tag_guid__tag_field="Season",
                tagxrecipe__txr_tag_guid__tag_name=current_season
            ).exclude(recipe_author=self.request.user).distinct()
            return recipes
        return Recipe.objects.none()[:int(n)]

    def __get_season_(self) -> str:
        today = date.today()
        seasons = [
            ('Primavera', (date(today.year, 3, 21), date(today.year, 6, 20))),
            ('Estate', (date(today.year, 6, 21), date(today.year, 9, 22))),
            ('Autunno', (date(today.year, 9, 23), date(today.year, 12, 20))),
            ('Inverno', (date(today.year, 1, 1), date(today.year, 3, 20))),
            ('Inverno', (date(today.year, 12, 21), date(today.year, 12, 31)))
        ]
        for season, (start, end) in seasons:
            if start <= today <= end:
                return season
        return None


class RecipeSearchView(View):
    def get(self, request):
        # Fetch RegisteredUser and check if it is suspended
        user_suspended = False
        try:
            reg_user = RegisteredUser.objects.get(user=request.user.id)
            user_suspended = check_user_suspension(reg_user)
        except RegisteredUser.DoesNotExist:
            reg_user = None
        form = SearchForm(request.GET or None, user=request.user, user_suspended=user_suspended, from_homepage=True)
        recipes = Recipe.objects.none()
        if form.is_valid():
            search_string = form.cleaned_data.get("search_string")
            # Check whether the user is authenticated AND is not suspended or not and eventually force the search parameter
            from_homepage = form.fields["from_homepage"]
            if request.user.is_authenticated and not user_suspended and from_homepage:
                search_param = form.cleaned_data.get("search_param")
                if not search_param:
                    search_param = "recipe_title"
            else:
                search_param = "recipe_title"
            # Perform the actual search
            if search_param == "recipe_title":
                recipes = Recipe.objects.filter(recipe_name__icontains=search_string).exclude(
                    Q(recipe_is_private=True) |
                    Q(recipe_author=self.request.user)
                )
            elif search_param == "author_name":
                recipes = Recipe.objects.filter(Q(recipe_author__first_name__icontains=search_string) | Q(recipe_author__last_name__icontains=search_string)).exclude(
                            Q(recipe_is_private=True) |
                            Q(recipe_author=self.request.user)
                        )
            elif search_param == "tag_name":
                recipes = Recipe.objects.filter(tagxrecipe__txr_tag_guid__tag_name__icontains=search_string).exclude(
                            Q(recipe_is_private=True) |
                            Q(recipe_author=self.request.user)
                        )
            elif search_param == "ingredient_name":
                ingredient_query = Ingredient.objects.filter(ingredient_name__icontains=search_string)
                recipes = Recipe.objects.filter(ingredientxrecipe__ixr_ingredient_guid__ingredient_name__icontains=search_string).exclude(
                            Q(recipe_is_private=True) |
                            Q(recipe_author=self.request.user)
                        )
                if reg_user and  not user_suspended and ingredient_query.exists():
                    ingredient = ingredient_best_match(search_string)
                    reg_user.reg_user_search_history["ingredients"] = ingredient.ingredient_name
                    reg_user.save()
        return render(request, template_name="search_results.html", context={"search_results": recipes, "form": form, "user": self.request.user, "reg_user": reg_user})
    

def ingredient_best_match(search_string):
    try:
        ingredients_matching = Ingredient.objects.get(ingredient_name=search_string)
        if ingredients_matching: 
            return ingredients_matching
    except Ingredient.DoesNotExist:
        ingredients_matching = Ingredient.objects.filter(ingredient_name__icontains=search_string)
        best_match = None
        best_ratio = 0
        for ingredient in ingredients_matching:
            current_ratio = thefuzz.fuzz.ratio(search_string.lower(), ingredient.ingredient_name.lower())
            if current_ratio > best_ratio:
                best_match = ingredient
                best_ratio = current_ratio
        return best_match
