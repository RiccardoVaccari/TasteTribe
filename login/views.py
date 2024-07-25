from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.edit import CreateView
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.contrib.auth import login
from google.auth.transport import requests
from google.oauth2 import id_token

from .models import *
from .forms import EditProfileForm

GOOGLE_CLIENT_ID = "253692078578-gti4mgr39kol8974nhnddi430qbjpkt3.apps.googleusercontent.com"


# Create your views here.
class UserRegistrationView(CreateView):
    form_class = UserCreationForm
    template_name = "usermanagement/user_registration.html"
    success_url = reverse_lazy("edit_profile")

    def form_valid(self, form):
        response = super().form_valid(form)
        user = form.instance
        login(self.request, user)
        return response


@login_required
def edit_profile(request):
    user = request.user
    try:
        reg_user = user.registereduser
    except RegisteredUser.DoesNotExist:
        reg_user = RegisteredUser(user=user)
    if request.method == "POST":
        form = EditProfileForm(request.POST, instance=reg_user, user=user)
        if form.is_valid():
            user.first_name = form.cleaned_data["first_name"]
            user.last_name = form.cleaned_data["last_name"]
            user.email = form.cleaned_data["email"]
            user.save()
            reg_user.reg_user_profile_pic = form.cleaned_data["reg_user_profile_pic"]
            reg_user.reg_user_about = form.cleaned_data["reg_user_about"]
            reg_user.reg_user_preferences = form.cleaned_data["reg_user_preferences"]
            form.save()
            return redirect(f"/profile/{user.id}/")
    else:
        form = EditProfileForm(instance=reg_user, user=user)
    return render(request, "usermanagement/user_profile_edit_page.html", {"form": form})


def profile_details(request, **kwargs):
    return render(request, "usermanagement/user_profile.html")


@csrf_exempt
def google_auth(request):
    token = request.POST.get("credential")
    try:
        user_data = id_token.verify_oauth2_token(token, requests.Request(), GOOGLE_CLIENT_ID)
    except ValueError:
        return HttpResponse("Invalid Google token", status=403)
    # Save user data in the session (might be useless in our case)
    request.session["user_data"] = user_data
    # Now we're going to create the user in order to store it in the database, but first we check if it's already in the database
    try:
        user = User.objects.get(email=user_data.get("email"))
    except User.DoesNotExist:
        user = User(
            first_name=user_data.get("given_name"),
            last_name=user_data.get("family_name"),
            email=user_data.get("email"),
            username=user_data.get("email").split("@")[0],
        )
        user.save()
        reg_user = RegisteredUser(user=user)
        reg_user.reg_user_profile_pic = user_data.get("picture")
        reg_user.save()
    # Lastly, we redirect the user to its profile page after logging it in
    login(request, user)
    return redirect(f"/profile/{user.id}/")
