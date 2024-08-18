import datetime
import uuid
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.views.generic import ListView, DetailView, CreateView
from django.views.generic.edit import FormMixin
from homepage.views import check_user_suspension
from .models import *
from .forms import *
from login.models import *


# Create your views here.
class ForumHomeView(ListView):
    model = ForumThread
    template_name = "forum_home.html"
    context_object_name = "fthreads"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            reg_user = RegisteredUser.objects.get(user=self.request.user.id)
            if check_user_suspension(reg_user):
                context["can_open_threads"] = False
            else:
                context["can_open_threads"] = True
        except RegisteredUser.DoesNotExist:
            context["can_open_threads"] = False
            reg_user = None
        context["user"] = self.request.user
        context["reg_user"] = reg_user
        return context


class ForumThreadCreateView(LoginRequiredMixin, CreateView):
    model = ForumThread
    form_class = ForumThreadCreationForm

    def form_valid(self, form):
        # Handle creation of thread (which is stored in form.instance)
        form.instance.fthread_creator = self.request.user
        form.instance.fthread_guid = uuid.uuid4()
        form.instance.fthread_creation_date = datetime.datetime.now()
        self.object = form.save()
        return JsonResponse({"fthread_guid": str(self.object.fthread_guid)})


class ForumThreadView(LoginRequiredMixin, FormMixin, ListView):
    model = ForumMessage
    template_name = "forum_thread.html"
    context_object_name = "fmessages"
    form_class = ForumMessageCreationForm

    def get_queryset(self):
        thread = get_object_or_404(ForumThread, fthread_guid=self.kwargs["thread_guid"])
        return ForumMessage.objects.filter(fmessage_thread_guid=thread).order_by("-fmessage_creation_date")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        thread = get_object_or_404(ForumThread, fthread_guid=self.kwargs["thread_guid"])
        context["forum_thread"] = thread
        context["form"] = self.get_form()
        # Fetch user interactions
        user_interactions = {}
        if self.request.user.is_authenticated:
            interactions = ForumMessageInteraction.objects.filter(interaction_user=self.request.user, interaction_fmessage__in=context["fmessages"])
            user_interactions = {interaction.interaction_fmessage_id: interaction.interaction_liked for interaction in interactions}
        for message in context["fmessages"]:
            message.user_interaction = user_interactions.get(message.id, 0)
        # Check for user suspension
        try:
            reg_user = RegisteredUser.objects.get(user=self.request.user.id)
            context["user_allowed"] = not check_user_suspension(reg_user)
        except RegisteredUser.DoesNotExist:
            context["user_allowed"] = False
            reg_user = None
        context["user"] = self.request.user
        context["reg_user"] = reg_user
        return context

    def post(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        thread = get_object_or_404(ForumThread, fthread_guid=self.kwargs["thread_guid"])
        fmessage = form.save(commit=False)
        fmessage.fmessage_thread_guid = thread
        fmessage.fmessage_author = self.request.user
        fmessage.fmessage_creation_date = datetime.datetime.now()
        fmessage.save()
        if self.request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({
                "message_id": fmessage.id,
                "message_content": fmessage.fmessage_content,
                "message_author": f"{fmessage.fmessage_author.first_name} {fmessage.fmessage_author.last_name}",
                "likes": fmessage.fmessage_up_votes,
                "dislikes": fmessage.fmessage_down_votes,
                "creation_date": fmessage.fmessage_creation_date
            })
        return redirect(reverse("forum_thread", kwargs={"thread_guid": thread.fthread_guid}))

@login_required
@require_POST
def toggle_message_interaction(request):
    # Fetch and organize needed data
    message_id = request.POST.get("message_id")
    interaction_type = request.POST.get("interaction_type")
    user = request.user
    fmessage = get_object_or_404(ForumMessage, id=message_id)
    interaction, created = ForumMessageInteraction.objects.get_or_create(interaction_fmessage=fmessage, interaction_user=user)
    user_interaction = elaborate_interaction(interaction, created, interaction_type)
    # Update up votes and down votes for the current message
    fmessage.fmessage_up_votes = ForumMessageInteraction.objects.filter(interaction_fmessage=fmessage, interaction_liked=INTERACTION_LIKE).count()
    fmessage.fmessage_down_votes = ForumMessageInteraction.objects.filter(interaction_fmessage=fmessage, interaction_liked=INTERACTION_DISLIKE).count()
    fmessage.save()
    return JsonResponse({
        "message_id": fmessage.id,
        "message_content": fmessage.fmessage_content,
        "message_author": f"{fmessage.fmessage_author.first_name} {fmessage.fmessage_author.last_name}",
        "likes": fmessage.fmessage_up_votes,
        "dislikes": fmessage.fmessage_down_votes,
        "creation_date": fmessage.fmessage_creation_date,
        "user_interaction": user_interaction
    })


# To be placed in a util file
def elaborate_interaction(interaction, created, interaction_type):
    # Parameter to pass to the frontend in order to render dynamically the like/dislike icons
    user_interaction = 0
    if interaction_type == "like":
        # If the interaction is new, then color the icon
        user_interaction = 1
        if not created and interaction.interaction_liked == INTERACTION_LIKE:
            # If the interaction was already the same, outline the icon
            user_interaction = 0
    elif interaction_type == "dislike":
        user_interaction = -1
        if not created and interaction.interaction_liked == INTERACTION_DISLIKE:
            user_interaction = 0
    # Handle the interaction to change, add or delete
    if interaction_type == "like":
        if interaction.interaction_liked == INTERACTION_LIKE:
            interaction.delete()
        else:
            interaction.interaction_liked = INTERACTION_LIKE
            interaction.save()
    elif interaction_type == "dislike":
        if interaction.interaction_liked == INTERACTION_DISLIKE:
            interaction.delete()
        else:
            interaction.interaction_liked = INTERACTION_DISLIKE
            interaction.save()
    return user_interaction
