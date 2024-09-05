from django.urls import path
from login.views import *

urlpatterns = [
    path("register/", UserRegistrationView.as_view(), name="register"),
    path("login/", TasteTribeLoginView.as_view(), name="login"),
    path("logout/", TasteTribeLogoutView.as_view(), name="logout"),
    path("logout/success/", logged_out, name="logged_out"),
    path("googleauth/", google_auth, name="googleauth"),
    path("change-pw/", TasteTribePwChangeView.as_view(), name="password_change"),
    path("profile/<int:user_id>/", profile_details, name="profile"),
    path("profile/", profile_details, name="profile"),
    path("profile/edit/", edit_profile, name="edit_profile"),
]