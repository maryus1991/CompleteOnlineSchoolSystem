from django.urls import path
from . import views

app_name = "user"

urlpatterns = [
    path("", views.UserListView.as_view() , name="list"),
    path("auth/", views.AuthView.as_view() , name="auth"),
    path("auth/login/", views.UserLoginView.as_view() , name="login")
]