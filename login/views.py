import random
import string
import jwt
from jwt.algorithms import RSAAlgorithm
import requests as py_requests
from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.core.cache import cache
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404, resolve_url
from django.contrib.auth.forms import UserCreationForm
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.edit import CreateView
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy, reverse
from django.contrib.auth import login
from google.auth.transport import requests
from google.oauth2 import id_token
from common.utils import generate_avatar, image_to_base64, url_to_base64
from forum.models import ForumThread
from homepage.models import Recipe
from quiz.models import Quiz
from .models import *
from .forms import EditProfileForm

GOOGLE_CLIENT_ID = "253692078578-gti4mgr39kol8974nhnddi430qbjpkt3.apps.googleusercontent.com"
GOOGLE_PUBLIC_KEYS_CACHE_KEY = "google_public_keys"
GOOGLE_PUBLIC_KEYS_CACHE_EXPIRY = 86400


# Create your views here.
class UserRegistrationView(CreateView):
    form_class = UserCreationForm
    template_name = "user_registration.html"
    success_url = reverse_lazy("edit_profile")

    def form_valid(self, form):
        response = super().form_valid(form)
        user = form.instance
        login(self.request, user)
        return response


class TasteTribeLoginView(LoginView):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            user_id = request.user.id
            return redirect(reverse("profile", kwargs={"user_id": user_id}))
        return super().dispatch(request, *args, **kwargs)
    
    def get_success_url(self):
        redirection_page = self.request.GET.get("next")
        if redirection_page:
            return resolve_url(redirection_page)
        user_id = self.request.user.id
        return reverse("profile", kwargs={"user_id": user_id})


class TasteTribeLogoutView(LogoutView):
    next_page = reverse_lazy("logged_out")


def logged_out(request):
    return render(request, template_name="logged_out.html")


class TasteTribePwChangeView(PasswordChangeView):
    success_url = reverse_lazy("profile")
    template_name = "password_change_form.html"


@login_required
def edit_profile(request):
    # Fetch eventual messages
    index = 0
    user_pw = None
    storage = messages.get_messages(request)
    for message in storage:
        if index == 0:
            user_pw = message.message
            break
        index += 1

    # Handle the user editing form
    user = request.user
    try:
        reg_user = user.registereduser
    except RegisteredUser.DoesNotExist:
        reg_user = RegisteredUser(user=user)

    if request.method == "POST":
        form = EditProfileForm(request.POST, request.FILES, instance=reg_user, user=user)
        if form.is_valid():
            user.first_name = form.cleaned_data["first_name"]
            user.last_name = form.cleaned_data["last_name"]
            user.email = form.cleaned_data["email"]
            user.username = form.cleaned_data["username"] 
            user.save()

            reg_user.reg_user_profile_pic = form.cleaned_data["reg_user_profile_pic"]
            if not reg_user.reg_user_profile_pic:
                reg_user.reg_user_profile_pic = image_to_base64(generate_avatar(user.first_name[0]))
            reg_user.reg_user_about = form.cleaned_data["reg_user_about"]
            reg_user.save()

            return redirect("profile", user_id=user.id)
    else:
        form = EditProfileForm(instance=reg_user, user=user)
        
    return render(request, "user_profile_edit_page.html", {"form": form, "user_pw": user_pw})


def profile_details(request, user_id=None):
    if user_id is None:
        if request.user.is_authenticated:
            user_id = request.user.id
        else:
            return redirect("login")
    user = get_object_or_404(User, id=user_id)
    reg_user = get_object_or_404(RegisteredUser, user=user)
    num_recipes_created = Recipe.objects.filter(recipe_author=user).count()
    num_quizzes_created = Quiz.objects.filter(quiz_author=user).count()
    num_threads_opened = ForumThread.objects.filter(fthread_creator=user).count()
    context = {
        "user": user,
        "reg_user": reg_user,
        "recipes": Recipe.objects.filter(recipe_author=user),
        "logged_user": request.user,
        "num_recipes_created": num_recipes_created,
        "num_quizzes_created": num_quizzes_created,
        "num_threads_opened": num_threads_opened,
    }
    return render(request, "user_profile.html", context)


# Views and functions to handle Google login
def fetch_google_public_keys():
    try:
        response = py_requests.get("https://www.googleapis.com/oauth2/v3/certs", timeout=5)
        response.raise_for_status()
        keys = response.json().get("keys", [])
        cache.set(GOOGLE_PUBLIC_KEYS_CACHE_KEY, keys, GOOGLE_PUBLIC_KEYS_CACHE_EXPIRY)
    except py_requests.RequestException:
        raise ValueError("Errore nella richiesta delle chiavi pubbliche di Google")


def google_token_local_verification(token):
    keys = cache.get(GOOGLE_PUBLIC_KEYS_CACHE_KEY)
    if not keys:
        fetch_google_public_keys()
        keys = cache.get(GOOGLE_PUBLIC_KEYS_CACHE_KEY)
    try:
        header = jwt.get_unverified_header(token)
        key = next((key for key in keys if key["kid"] == header["kid"]), None)
        if not key:
            raise ValueError("Public key not found for the given token.")
        public_key = RSAAlgorithm.from_jwk(key)
        decoded_token = jwt.decode(token, key=public_key, audience=GOOGLE_CLIENT_ID, algorithms=["RS256"])
        return decoded_token
    except jwt.PyJWTError:
        # Use Google API Verification exclusively if local cached verification fails
        return id_token.verify_oauth2_token(token, requests.Request(), GOOGLE_CLIENT_ID)


@csrf_exempt
def google_auth(request):
    token = request.POST.get("credential")
    if not token:
        return HttpResponse("No token provided", status=400)
    try:
        user_data = google_token_local_verification(token)
    except ValueError:
        return HttpResponse("Invalid Google token", status=403)
    # Now we're going to create the user in order to store it in the database, but first we check if it's already in the database
    is_new_user = False
    try:
        user = User.objects.get(email=user_data.get("email"))
        login(request, user)
    except User.DoesNotExist:
        is_new_user = True
    if is_new_user:
        create_new_user(user_data, request)
        return redirect("/profile/edit/")
    next_url = request.POST.get("next", "/")
    return redirect(next_url)


def create_new_user(user_data, request):
    user = User(
        first_name=user_data.get("given_name"),
        last_name=user_data.get("family_name"),
        email=user_data.get("email"),
        username=user_data.get("email").split("@")[0],
    )
    characters = string.ascii_letters + string.digits + string.punctuation
    password = "".join(random.choice(characters) for i in range(8))
    user.set_password(password)
    user.save()
    reg_user = RegisteredUser(user=user)
    reg_user.reg_user_profile_pic = url_to_base64(user_data.get("picture"))
    reg_user.save()
    messages.success(request, password)
    login(request, user)
