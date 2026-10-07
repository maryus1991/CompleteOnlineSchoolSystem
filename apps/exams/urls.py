from django.urls import path
from . import views

app_name = 'exam'

urlpatterns = [
    path('', views.ExamListView.as_view(), name='list'),
    path('<int:pk>/', views.ExamDetailsView.as_view(), name='details'),
    path('<int:pk>/set-exam-informations/', views.SetExamInformationView.as_view(), name='exam-information'),
    path('<int:pk>/start-exam/', views.SetExamInformationView.as_view(), name='exam-start'),
    path('<int:pk>/start-exam/<int:question_id>/', views.SetExamInformationView.as_view(), name='exam-start-with-question-id'),
    path('<int:pk>/exam-answer/<int:question_id>/<int:option_id>/', views.ExamSetAnswerOptions.as_view(), name='exam-set-option'),
    path('<int:pk>/set-skipped/<int:question_id>/', views.ExamSetSkippedToQuestion.as_view(), name='exam-set-skipped'),
    path('<int:pk>/finished/', views.ExamFinished.as_view(), name='exam-finished'),
]