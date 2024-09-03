"""
URL configuration for TasteTribe project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path
from collectionz.views import *
from homepage.views import *
from recipedetail.views import *
from login.views import *
from quiz.views import *
from forum.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    re_path(r"^$|^/$|^home/?$|^homepage/?$", HomepageView.as_view(), name="homepage"),
    re_path(r"^search$|^search/$|^home/search/?$|^homepage/search/?$", RecipeSearchView.as_view(), name="search"),
    path("recipe/<uuid:recipe_guid>/", RecipeDetailView.as_view(), name="recipe_details"),
    path("recipe/<uuid:recipe_guid>/edit", RecipeEditView.as_view(), name="recipe_edit"),
    path("recipe/<uuid:recipe_guid>/delete", delete_recipe, name='delete_recipe'),
    path('recipe/<uuid:recipe_guid>/add_review/', add_review, name='add_review'),
    path("recipe/toggle_interaction", toggle_review_interaction, name="review_interaction"),
    path("recipe/create/", RecipeCreateView.as_view(), name="recipe_create"),
    path('recipe/create/from/<uuid:recipe_guid>/', RecipeCreateView.as_view(), name='recipe_create_from_existing'),
    path("check-ingredient/", check_ingredient, name="check_ingredient"),
    path("register/", UserRegistrationView.as_view(), name="register"),
    path("login/", TasteTribeLoginView.as_view(), name="login"),
    path("logout/", TasteTribeLogoutView.as_view(), name="logout"),
    path("profile/<int:user_id>/", profile_details, name="profile"),
    path("profile/", profile_details, name="profile"),
    path("profile/edit/", edit_profile, name="edit_profile"),
    path("googleauth/", google_auth, name="googleauth"),
    path("change-pw/", TasteTribePwChangeView.as_view(), name="password_change"),
    path("quiz/", QuizListView.as_view(), name="quiz_home"),
    path("quiz/create/", QuizCreationView.as_view(), name="quiz_creation"),
    path("quiz/play/<uuid:quiz_guid>/", play_quiz, name="quiz_game"),
    path("forum/", ForumHomeView.as_view(), name="forums"),
    path("forum/create/", ForumThreadCreateView.as_view(), name="forum_create_thread"),
    path("forum/thread/<uuid:thread_guid>/", ForumThreadView.as_view(), name="forum_thread"),
    path("forum/thread/toggle_interaction/", toggle_message_interaction, name="toggle_interaction"),
    path("collections/", CollectionsView.as_view(), name="collections"),
    path("collections/<uuid:collection_guid>/", CollectionDetailView.as_view(), name="collection_details"),
    path("delete-from-collection/", delete_recipe_from_collection, name="delete_from_collection"),
    path("add-to-collection/", add_to_collection, name="add_to_collection"),
    path('check-recipe-in-collection/', check_recipe_in_collection, name='check_recipe_in_collection'),

]
