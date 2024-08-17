import datetime
import uuid
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.files.base import ContentFile
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import ListView, DetailView
from django.views.generic.edit import FormMixin
from homepage.forms import SearchForm
from homepage.views import check_user_suspension
from .models import *
from .forms import *


# Create your views here.
class CollectionsView(LoginRequiredMixin, FormMixin, ListView):
    model = RecipesCollection
    template_name = "collections.html"
    form_class = CollectionCreationForm
    success_url = reverse_lazy("collections")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Fetch the collections created by the currently logged user
        context["user_collections"] = RecipesCollection.objects.filter(collection_author=self.request.user)
        # Fetch the collections that haven't been created by the user
        context["other_collections"] = RecipesCollection.objects.filter(~Q(collection_author=self.request.user))
        return context

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            collection = form.save(commit=False)
            collection_creation(collection, request)
            # After performing all the necessary information, redirect to success url
            return redirect(self.get_success_url())
        else:
            return self.form_invalid(form)


class CollectionDetailView(DetailView):
    model = RecipesCollection
    template_name = "collection_details.html"
    context_object_name = "collection"
    pk_url_kwarg = "collection_guid"
    form = SearchForm()

    def get_form(self):
        reg_user = RegisteredUser.objects.get(user=self.request.user.id)
        user_suspended = check_user_suspension(reg_user)
        return SearchForm(user=self.request.user, user_suspended=user_suspended, from_homepage=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Fetch collection related data
        collection_guid_string = self.kwargs.get(self.pk_url_kwarg)
        context["collection"] = RecipesCollection.objects.get(collection_guid=collection_guid_string)
        # Fetch recipes stored in collection
        recipes_guids = RecipeXCollection.objects.filter(rxc_collection_guid=collection_guid_string)
        recipes = Recipe.objects.filter(recipe_guid__in=recipes_guids.values_list("rxc_recipe_guid", flat=True))
        context["recipes"] = recipes
        # The search form will be displayed only if a user is exploring its own collections
        context["form"] = self.get_form()
        context["user"] = self.request.user
        return context


@require_POST
def delete_recipe_from_collection(request):
    collection_guid = request.POST.get("collection_guid")
    recipe_guid = request.POST.get("recipe_guid")
    try:
        collection = RecipesCollection.objects.get(collection_guid=collection_guid)
        recipe = Recipe.objects.get(recipe_guid=recipe_guid)
        RecipeXCollection.objects.filter(rxc_collection_guid=collection, rxc_recipe_guid=recipe).delete()
        return JsonResponse({"success": True})
    except (RecipesCollection.DoesNotExist, Recipe.DoesNotExist):
        return JsonResponse({"success": False, "error": "Invalid collection or recipe"}, status=400)


# To be transferred to a utils file
def collection_creation(collection, request):
    collection.collection_guid = uuid.uuid4()
    collection.collection_author = request.user
    collection.collection_creation_date = datetime.datetime.now()
    # Handle base64 image conversion
    b64_collection_cover = request.POST.get("collection_cover")
    if b64_collection_cover:
        image_data = base64.b64decode(b64_collection_cover.split(',')[1])
        image_file = ContentFile(image_data, name='collection_cover.png')
        collection.collection_cover = image_file
    collection.save()
