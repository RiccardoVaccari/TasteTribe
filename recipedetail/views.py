from uuid import uuid4
from datetime import date
from django.views.generic import DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404

from .models import Recipe
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

    def form_valid(self, form):
        recipe: Recipe = form.instance
        recipe.recipe_guid = uuid4()
        recipe.recipe_prep_time = f"{form.cleaned_data.get("hours")}:{form.cleaned_data.get("minutes")}"
        recipe.recipe_author = self.request.user
        recipe.recipe_creation_date = date.today()
        form.instance = recipe
        return super().form_valid(form)
    
    def get_success_url(self) -> str:
        recipe = self.object
        return f"/recipe/{self.object.pk}"

    