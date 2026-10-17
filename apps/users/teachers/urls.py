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

    # questions
    path("questions/", views.questions.QuestionListView.as_view(), name="question-list"),
    path("questions/create/", views.questions.QuestionCreateView.as_view(), name="question-create"),
    path("questions/update/<int:pk>/", views.questions.QuestionUpdateView.as_view(), name="question-update"),
    path("questions/delete/<int:pk>/", views.questions.QuestionDeleteView.as_view(), name="question-delete"),
    path("questions/publish/<int:pk>/", views.questions.AddQuestionToQbankView.as_view(), name="question-publish"),

    # exam

    path("exams/", views.exam.ExamListView.as_view(), name="exam-list"),
    path("exams/create/", views.exam.ExamCreateView.as_view(), name="exam-create"),
    path("exams/update/<int:pk>/", views.exam.ExamUpdateView.as_view(), name="exam-update"),
    path("exams/delete/<int:pk>/", views.exam.ExamDeleteView.as_view(), name="exam-delete"),
    path("exams/<int:pk>/students/", views.exam.ExamAddAndRemoveStudentView.as_view(), name="exam-students"),
    path("exams/<int:pk>/questions/", views.exam.ExamAddAndRemoveQuestionsView.as_view(), name="exam-questions"),

]