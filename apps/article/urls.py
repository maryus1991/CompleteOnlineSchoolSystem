from django.urls import path
from . import views

app_name = "article"

urlpatterns = [
    path('', views.ArticleListView.as_view(), name='article-list'),
    path('category-posts-list/<int:pk>/', views.ArticleCategoryListView.as_view(), name='article-category-list'),
    path('<int:pk>/', views.ArticleDetailView.as_view(), name='article-details'),
    path('<int:pk>/rate/', views.ArticleRateView.as_view(), name='article-rate'),
    path('<int:pk>/comment/', views.ArticleCommentCreateView.as_view(), name='article-comment'),
    path('<int:pk>/comment/<int:comment_pk>/delete/', views.ArticleCommentDeleteView.as_view(), name='article-comment-delete'),
]
