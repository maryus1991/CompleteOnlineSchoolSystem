from django.urls import path
from . import views

app_name = 'class'

urlpatterns = [
    path('', views.ClassListView.as_view(), name='list'),
    path('<int:pk>', views.ClassDetailView.as_view(), name='details'),



]