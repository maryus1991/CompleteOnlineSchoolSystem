from django.urls import path
from . import views

app_name = "article"

urlpatterns = [
    path('', views.ArticleListView.as_view(), name='article-list'),
    path('category-posts-list/<int:pk>/', views.ArticleCategoryListView.as_view(), name='article-category-list'),
    path('<int:pk>/', views.ArticleListView.as_view(), name='article-details'),
]