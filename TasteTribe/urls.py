"""
URL configuration for TasteTribe project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path
from django.contrib.auth import views as auth_views
from recipedetail.views import *
from login.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path("recipe/<uuid:recipe_guid>/", RecipeDetailView.as_view(), name="recipe_details"),
    path("register/", UserRegistrationView.as_view(), name="register"),
    path("login/", TasteTribeLoginView.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("profile/<int:user_id>/", profile_details, name="profile"),
    path("profile/edit/", edit_profile, name="edit_profile"),
    path("googleauth/", google_auth, name="googleauth")
]
