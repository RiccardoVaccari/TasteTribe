from django.urls import path, re_path
from homepage.views import *

urlpatterns = [
    re_path(r"^$|^/$|^home/?$|^homepage/?$", HomepageView.as_view(), name="homepage"),
    re_path(r"^search$|^search/$|^home/search/?$|^homepage/search/?$", RecipeSearchView.as_view(), name="search"),
]