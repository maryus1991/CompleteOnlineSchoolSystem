from . import views
from django.urls import path

app_name = 'site'

urlpatterns = [
    path('', views.Main.as_view(), name='main'),
    path('contact/', views.Contact.as_view(), name='contact'),
    path('free-counseling/', views.Counseling.as_view(), name='counseling'),
    path('faq/', views.FAQListView.as_view(), name='faq'),
    path('about/', views.About.as_view(), name='about'),
]