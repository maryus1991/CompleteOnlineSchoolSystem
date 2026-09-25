from . import views
from django.urls import path

app_name = 'site'

urlpatterns = [
    path('', views.Main.as_view(), name='main'),
    path('contact/', views.Contact.as_view(), name='contact'),
    # path('about/', views.About.as_view(), name='about'),
]