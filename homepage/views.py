from django.db.models import Q
from django.shortcuts import render, redirect
from django.views.generic import View
from .forms import *
from .models import Recipe
from django.http import JsonResponse, HttpResponse
import json


# Create your views here.
def home_page_view(request):
    form = SearchForm(user=request.user)
    return render(request, template_name="homepage.html", context={"form": form})


class RecipeSearchView(View):

    def get(self, request):
        form = SearchForm(request.GET or None, user=request.user)
        recipes = Recipe.objects.none()
        if form.is_valid():
            search_string = form.cleaned_data.get("search_string")
            # Check whether the user is authenticated or not and eventually force the search parameter
            if request.user.is_authenticated:
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
                recipes = Recipe.objects.filter(ingredientxrecipe__ixr_ingredient_guid__ingredient_name__icontains=search_string)
        return render(request, template_name="search_results.html", context={"search_results": recipes, "form": form})
