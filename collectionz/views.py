from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import render
from django.views.generic import ListView
from .models import *


# Create your views here.
class CollectionsView(LoginRequiredMixin, ListView):
    model = RecipesCollection
    template_name = "collections.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Fetch the collections created by the currently logged user
        context["user_collections"] = RecipesCollection.objects.filter(collection_author=self.request.user)
        # Fetch the collections that haven't been created by the user
        context["other_collections"] = RecipesCollection.objects.filter(~Q(collection_author=self.request.user))
        return context
