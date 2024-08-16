import datetime
import uuid
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.files.base import ContentFile
from django.db.models import Q
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView
from django.views.generic.edit import FormMixin
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
            # After performing all the necessary information, redirect to success url
            return redirect(self.get_success_url())
        else:
            return self.form_invalid(form)
