from django.shortcuts import render, redirect
from .forms import *
from .models import Recipe
from django.http import JsonResponse, HttpResponse
import json


# Create your views here.
def home_page_view(request):
    form = SearchForm()
    return render(request, template_name="homepage/homepage.html", context={"form": form})


def search(request):
    if request.method == "GET":
        form = SearchForm(request.GET)
        if form.is_valid():
            recipe_list = Recipe.objects.filter(recipe_name__contains=form.cleaned_data["search_string"]).values()
            return JsonResponse(list(recipe_list), safe=False)
    return HttpResponse("error", status=400)
