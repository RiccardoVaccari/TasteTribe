from django.urls import path
from recipedetail.views import *

urlpatterns = [
    path("recipe/<uuid:recipe_guid>/", RecipeDetailView.as_view(), name="recipe_details"),
    path("recipe/<uuid:recipe_guid>/edit", RecipeEditView.as_view(), name="recipe_edit"),
    path("recipe/<uuid:recipe_guid>/delete", delete_recipe, name='delete_recipe'),
    path('recipe/<uuid:recipe_guid>/add_review/', add_review, name='add_review'),
    path("recipe/toggle_interaction", toggle_review_interaction, name="review_interaction"),
    path("recipe/create/", RecipeCreateView.as_view(), name="recipe_create"),
    path('recipe/create/from/<uuid:recipe_guid>/', RecipeCreateView.as_view(), name='recipe_create_from_existing'),
    path("check-ingredient/", check_ingredient, name="check_ingredient"),
    path("add-to-collection/", add_to_collection, name="add_to_collection"),
]