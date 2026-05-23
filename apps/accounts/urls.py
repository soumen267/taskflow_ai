from django.urls import path

from apps.accounts.forms import CustomAuthenticationForm
from . import views

app_name = "accounts"

urlpatterns = [
    path("login/", views.LoginView.as_view(authentication_form=CustomAuthenticationForm), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("profile/", views.ProfileView.as_view(), name="profile"),
]
