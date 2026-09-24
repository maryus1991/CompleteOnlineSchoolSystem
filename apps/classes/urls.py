from django.urls import path
from . import views

app_name = 'class'

urlpatterns = [
    path('', views.ClassListView.as_view(), name='list'),
    path('<int:pk>', views.ClassDetailView.as_view(), name='details'),

    path('category/major/list', views.ClassListView.as_view(), name='category-major-list'),
    path('category/grade/list', views.ClassListView.as_view(), name='category-grade-list'),
    path('category/lesson/list', views.ClassListView.as_view(), name='category-lesson-list'),

]