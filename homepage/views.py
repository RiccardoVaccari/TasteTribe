import random
from datetime import date
from typing import Any
from django.views.generic import ListView
from django.http import JsonResponse, HttpResponse

from recipedetail.models import Ingredient
from login.models import RegisteredUser

from .forms import SearchForm
from .models import Recipe


class HomepageView(ListView):
    model = Recipe
    template_name = 'homepage.html'
    context_object_name = 'recipes'
    form = SearchForm()

    def get_queryset(self):
        all_ids = Recipe.objects.filter(
            recipe_is_private=False).exclude(recipe_author=self.request.user).values_list('recipe_guid', flat=True)
        all_ids = list(all_ids)
        if len(all_ids) > 200:
            all_ids = random.sample(all_ids, 200)
        else:
            random.shuffle(all_ids)

        return Recipe.objects.filter(recipe_guid__in=all_ids)
    
    def get_form(self):
        return SearchForm()

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['form'] = self.get_form()
        
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


def search(request):
    if request.method == "GET":
        form = SearchForm(request.GET)
        if form.is_valid():
            recipe_list = Recipe.objects.filter(recipe_name__contains=form.cleaned_data["search_string"]).values()
            return JsonResponse(list(recipe_list), safe=False)
    return HttpResponse("error", status=400)