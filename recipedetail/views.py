from django.shortcuts import render
from django.views.generic import DetailView
from .models import *


# RECIPE DETAILS APP - VIEWS
class RecipeDetailView(DetailView):
    model = Recipe
    template_name = "recipedetails/recipe_details.html"

    def get_context_data(self, **kwargs):
        pass  # Yet to be defined

    def get_queryset(self):
        return self.model.objects.filter(recipe_guid=self.request.GET.get("recipe_guid"))
