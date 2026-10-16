from django.urls import path
from . import views

app_name = 'teacher'

urlpatterns = [
    path("", views.main.MainView.as_view(), name="main"),
    path("account/", views.main.EditAccountView.as_view(), name="account"),

    # tickets
    path('tickets/', views.ticket.TicketListView.as_view(), name='ticket-list'),
    path('tickets/create/', views.ticket.TicketCreateView.as_view(), name='ticket-create'),
    path('tickets/<int:pk>', views.ticket.TicketChatView.as_view(), name='ticket-chat'),

    # article
    path('article/', views.article.ArticleListView.as_view(), name='article-list'),
    path('article/create/', views.article.ArticleCreateView.as_view(), name='article-create'),
    path('article/update/<int:pk>', views.article.ArticleUpdateView.as_view(), name='article-update'),
    path('article/delete/<int:pk>', views.article.ArticleDeleteView.as_view(), name='article-delete'),

]