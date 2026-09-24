from django.urls import path
from . import views

app_name = 'exam'

urlpatterns = [
    path('', views.ExamListView.as_view(), name='list'),
    path('<int:pk>', views.ExamListView.as_view(), name='details'),
]