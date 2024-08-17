import random
from datetime import date, datetime
import time
from typing import Any
from django.shortcuts import render
from django.views.generic import ListView, View
from django.db.models import Q

from recipedetail.models import Ingredient
from login.models import RegisteredUser

from .forms import SearchForm
from .models import Recipe, Tag
from utils import check_user_suspension


class HomepageView(ListView):
    model = Recipe
    template_name = 'homepage.html'
    context_object_name = 'recipes'
    form = SearchForm()

    def dispatch(self, request, *args, **kwargs):
        self.update_notifications()
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        if self.request.user and self.request.user.is_authenticated and not self.user_suspended:
            all_ids = Recipe.objects.filter(
                recipe_is_private=False).exclude(recipe_author=self.request.user).values_list('recipe_guid', flat=True)
        else:
            all_ids = Recipe.objects.filter(recipe_is_private=False).values_list('recipe_guid', flat=True)
        
        all_ids = list(all_ids)
        if len(all_ids) > 200:
            all_ids = random.sample(all_ids, 200)
        else:
            random.shuffle(all_ids)

        return Recipe.objects.filter(recipe_guid__in=all_ids)
    
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

        if self.request.user and self.request.user.is_authenticated and not self.user_suspended:
            context["latest_recipes"] = self.get_latest_publish()

            latest_ingredients = RegisteredUser.objects.get(
                user=self.request.user).reg_user_search_history.get("ingredients")
            if not latest_ingredients:
                context["ingredient_recipes"] = None
            else:
                latest_ingredient_name = latest_ingredients[0]
                context["ingredient_name"] = latest_ingredient_name
                context["ingredient_recipes"] = self.get_recipes_by_ingredient(
                    latest_ingredient_name)

            season = self.__get_season_()
            context["season"] = season
            context["season_recipes"] = self.get_recipes_by_season(season)

        return context

    def get_latest_publish(self, n: int = 20):
        return Recipe.objects.order_by('-recipe_creation_date')[:int(n)]

    def get_recipes_by_ingredient(self, ingredient_name: str, n: int = 20):
        try:
            ingredient = Ingredient.objects.get(
                ingredient_name=ingredient_name)
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
            pass
        form = SearchForm(request.GET or None, user=request.user, user_suspended=user_suspended, from_homepage=True)
        recipes = Recipe.objects.none()
        if form.is_valid():
            search_string = form.cleaned_data.get("search_string")
            # Check whether the user is authenticated AND is not suspended or not and eventually force the search parameter
            from_homepage = form.cleaned_data.get("from_homepage", True)
            if request.user.is_authenticated and not user_suspended and from_homepage:
                search_param = form.cleaned_data.get("search_param")
            else:
                search_param = "recipe_title"
            # Perform the actual search
            if search_param == "recipe_title":
                recipes = Recipe.objects.filter(recipe_name__icontains=search_string)
            elif search_param == "author_name":
                recipes = Recipe.objects.filter(Q(recipe_author__first_name__icontains=search_string) | Q(recipe_author__last_name__icontains=search_string))
            elif search_param == "tag_name":
                recipes = Recipe.objects.filter(tagxrecipe__txr_tag_guid__tag_name__icontains=search_string)
            elif search_param == "ingredient_name":
                ingredient_query = Ingredient.objects.filter(ingredient_name__icontains=search_string)
                recipes = Recipe.objects.filter(ingredientxrecipe__ixr_ingredient_guid__ingredient_name__icontains=search_string)

                if reg_user and  not user_suspended and ingredient_query.exists():
                    ingredient = ingredient_query.first()
                    ingredients = reg_user.reg_user_search_history["ingredients"]
                    ingredients.insert(0, ingredient.ingredient_name)
                    reg_user.reg_user_search_history["ingredients"] = list(set(ingredients))[:10]
                    reg_user.save()

        return render(request, template_name="search_results.html", context={"search_results": recipes, "form": form})
    