import datetime
from django.db.models import Q
from django.shortcuts import render, redirect
from django.views.generic import View
from login.models import RegisteredUser
from .forms import *
from .models import Recipe
from django.http import JsonResponse, HttpResponse
import json


# Create your views here.
def home_page_view(request):
    # Preliminary operations: check if the user is authenticated and eventually display notifications for him
    notifications_to_read = []
    try:
        reg_user = RegisteredUser.objects.get(user=request.user.id)
        notifications_to_read = reg_user.reg_user_status.get("notifications", [])
        reg_user.reg_user_status["notifications"] = []  # Reset the notifications since they have been shown to the user
        reg_user.save()
        user_suspended = check_user_suspension(reg_user)
    except RegisteredUser.DoesNotExist:
        user_suspended = False
    # Display the search form to allow the user to search for recipes
    form = SearchForm(user=request.user, user_suspended=user_suspended)
    return render(request, template_name="homepage.html", context={"form": form, "user": request.user, "notifications": notifications_to_read})


class RecipeSearchView(View):
    def get(self, request):
        # Fetch RegisteredUser and check if it is suspended
        user_suspended = False
        try:
            reg_user = RegisteredUser.objects.get(user=request.user.id)
            user_suspended = check_user_suspension(reg_user)
        except RegisteredUser.DoesNotExist:
            pass
        form = SearchForm(request.GET or None, user=request.user, user_suspended=user_suspended)
        recipes = Recipe.objects.none()
        if form.is_valid():
            search_string = form.cleaned_data.get("search_string")
            # Check whether the user is authenticated AND is not suspended or not and eventually force the search parameter
            if request.user.is_authenticated and not user_suspended:
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


def check_user_suspension(reg_user):
    suspension = reg_user.reg_user_status["is_suspended"]
    # Check whether to remove suspension if it ended
    if suspension:
        suspension_end = datetime.datetime.strptime(reg_user.reg_user_status["suspension_end"], "%Y-%m-%d")
        if suspension_end <= datetime.datetime.now():
            # Suspension ended so we reset the user status
            reg_user.reg_user_status["is_suspended"] = False
            reg_user.reg_user_status["suspension_end"] = None
            reg_user.save()
            return False
        else:
            return True
    else:
        return False
