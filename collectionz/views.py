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
from homepage.models import Tag
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
        user_collections = RecipesCollection.objects.filter(collection_author=self.request.user)
        context["user_collections"] = user_collections
        # Fetch the collections that haven't been created by the user and are not private
        other_collections = RecipesCollection.objects.filter(~Q(collection_author=self.request.user), collection_is_private=False)

        # Code that implements the RS for collections
        # First of all we create a set of all the tags that are present in the user's collections
        user_collections_tag_set = generate_tag_set(user_collections)
        # Now that the set is created we proceed to create an ordered set with the recommended collections
        recommended_collections = []
        other_collections_matched_tags = []
        for collection in other_collections:
            collection_tag_set = generate_tag_set([collection])
            tags_difference = len(user_collections_tag_set.difference(collection_tag_set))
            other_collections_matched_tags.append({"collection": collection, "tags_difference": tags_difference})
        # Now that we compiled the list, we order it from the least different to the most different
        other_collections_matched_tags = sorted(other_collections_matched_tags, key=lambda d: d.get("tags_difference"))
        # Display only 5 recommended collections (this number might be varied in the future)
        count = 0
        for rec_coll in other_collections_matched_tags:
            if rec_coll not in recommended_collections:
                count += 1
                recommended_collections.append(rec_coll.get("collection"))
            if count == 5:
                break
        rec_collections_guids = []
        for rec_coll in recommended_collections:
            rec_collections_guids.append(rec_coll.collection_guid)
        recommended_collections_set = RecipesCollection.objects.filter(collection_guid__in=rec_collections_guids)
        context["recommended_collections"] = recommended_collections_set
        # Clean the "other collections" list from the recommended collections
        other_collections = RecipesCollection.objects.filter(~Q(collection_author=self.request.user), collection_is_private=False).exclude(collection_guid__in=rec_collections_guids)
        context["other_collections"] = other_collections

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


# To be transferred to a utils file
def generate_tag_set(collections):
    collections_tag_set = set()
    if collections:
        recipes_set = set()
        for collection in collections:
            # Fetch all recipes filtering by the collection guid
            recipes = Recipe.objects.filter(recipexcollection__rxc_collection_guid=collection.collection_guid)
            for recipe in recipes:
                recipes_set.add(recipe)
        # Right after fetching the recipes, proceed with the creation of the tag set
        for recipe in recipes_set:
            tags = Tag.objects.filter(tagxrecipe__txr_recipe_guid=recipe.recipe_guid)
            for tag in tags:
                collections_tag_set.add(tag)
    return collections_tag_set
