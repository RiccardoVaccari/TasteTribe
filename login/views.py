import base64

from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.views.generic.edit import CreateView
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.contrib.auth import login
from .models import *
from .forms import EditProfileForm


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
