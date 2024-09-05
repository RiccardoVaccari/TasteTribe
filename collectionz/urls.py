from django.urls import path
from collectionz.views import *

urlpatterns = [
    path("collections/", CollectionsView.as_view(), name="collections"),
    path("collections/<uuid:collection_guid>/", CollectionDetailView.as_view(), name="collection_details"),
    path("delete-from-collection/", delete_recipe_from_collection, name="delete_from_collection"),
    path('check-recipe-in-collection/', check_recipe_in_collection, name='check_recipe_in_collection'),
]