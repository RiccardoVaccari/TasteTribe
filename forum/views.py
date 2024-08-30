from datetime import datetime 
import uuid
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.views.generic import ListView, DetailView, CreateView
from django.views.generic.edit import FormMixin
from common.utils import *
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

        fthreads = context['fthreads']  # Ottieni i thread dal contesto esistente
        for thread in fthreads:
            # Recupera l'ultimo messaggio per ogni thread
            latest_message = ForumMessage.objects.filter(fmessage_thread_guid=thread).order_by('-fmessage_creation_date').first()
            thread.latest_message = latest_message  # Aggiungi l'ultimo messaggio come attributo al thread
            thread.responses_count = ForumMessage.objects.filter(fmessage_thread_guid=thread).count()
            thread.reg_user = RegisteredUser.objects.get(user_id=thread.fthread_creator)

        return context


class ForumThreadCreateView(LoginRequiredMixin, CreateView):
    model = ForumThread
    form_class = ForumThreadCreationForm

    def form_valid(self, form):
        # Handle creation of thread (which is stored in form.instance)
        form.instance.fthread_creator = self.request.user
        form.instance.fthread_guid = uuid.uuid4()
        form.instance.fthread_creation_date = datetime.now()
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
            interactions = ForumMessageInteraction.objects.filter(
                interaction_user=self.request.user,
                interaction_fmessage__in=context["fmessages"]
            )
            user_interactions = {interaction.interaction_fmessage_id: interaction.interaction_liked for interaction in interactions}

        # Fetch all RegisteredUsers for the message authors
        authors_ids = [message.fmessage_author_id for message in context["fmessages"]]
        registered_users = RegisteredUser.objects.filter(user_id__in=authors_ids)
        reg_user_dict = {reg_user.user_id: reg_user for reg_user in registered_users}

        # Attach user_interaction and reg_user to each message
        for message in context["fmessages"]:
            message.user_interaction = user_interactions.get(message.id, 0)
            message.reg_user = reg_user_dict.get(message.fmessage_author_id)  # Add reg_user to each message

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
    
    def form_invalid(self, form):
        # Log dell'errore di validazione del form
        import logging
        logger = logging.getLogger(__name__)
        logger.error("Form invalid: %s", form.errors)
        
        # Debug della richiesta
        logger.debug("Form data: %s", self.request.POST)
        
        # Ritorna il form non valido
        if self.request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({
                "error": form.errors,
                "message": "There was an error with your submission."
            }, status=400)
        
        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):
        thread = get_object_or_404(ForumThread, fthread_guid=self.kwargs["thread_guid"])
        fmessage = form.save(commit=False)
        fmessage.fmessage_thread_guid = thread
        fmessage.fmessage_author = self.request.user
        fmessage.fmessage_creation_date = datetime.now()
        fmessage.save()

        # Attempt to get user's profile picture
        try:
            reg_user = RegisteredUser.objects.get(user=fmessage.fmessage_author)
            user_profile_pic = reg_user.reg_user_profile_pic
        except RegisteredUser.DoesNotExist:
            user_profile_pic = ""

        # Check for AJAX request using request.is_ajax() or the preferred method in Django versions > 3.1
        if self.request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({
                "message_id": fmessage.id,
                "message_content": fmessage.fmessage_content,
                "message_author": f"{fmessage.fmessage_author.first_name} {fmessage.fmessage_author.last_name}",
                "likes": fmessage.fmessage_up_votes,
                "dislikes": fmessage.fmessage_down_votes,
                "creation_date": fmessage.fmessage_creation_date.strftime('%d/%m/%Y %H:%M'),
                "user_profile_pic": user_profile_pic,
            })
        
        # For non-AJAX requests
        return redirect(reverse("forum_thread", kwargs={"thread_guid": thread.fthread_guid}))


@login_required
@require_POST
def toggle_message_interaction(request):
    message_id = request.POST.get("message_id")
    interaction_type = request.POST.get("interaction_type")
    user = request.user

    fmessage = get_object_or_404(ForumMessage, id=message_id)
    
    try:
        reg_user = RegisteredUser.objects.get(user=user)
    except RegisteredUser.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=400)

    # Get or create interaction object
    interaction, created = ForumMessageInteraction.objects.get_or_create(
        interaction_fmessage=fmessage,
        interaction_user=user
    )
    
    # Determine the current interaction
    if interaction.interaction_liked == INTERACTION_LIKE:
        if interaction_type == 'like':
            interaction.delete()  # Remove like
            user_interaction = 0
        else:
            interaction.interaction_liked = INTERACTION_DISLIKE
            interaction.save()
            user_interaction = -1
    elif interaction.interaction_liked == INTERACTION_DISLIKE:
        if interaction_type == 'dislike':
            interaction.delete()  # Remove dislike
            user_interaction = 0
        else:
            interaction.interaction_liked = INTERACTION_LIKE
            interaction.save()
            user_interaction = 1
    else:
        if interaction_type == 'like':
            interaction.interaction_liked = INTERACTION_LIKE
            user_interaction = 1
        elif interaction_type == 'dislike':
            interaction.interaction_liked = INTERACTION_DISLIKE
            user_interaction = -1
        interaction.save()
    
    # Update up votes and down votes
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
        "user_interaction": user_interaction,
        "user_profile_pic": reg_user.reg_user_profile_pic
    })