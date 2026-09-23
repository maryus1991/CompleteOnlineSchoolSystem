from . import views
from django.urls import path

urlpatterns = [
    path('', views.Main.as_view(), name='main'),
]