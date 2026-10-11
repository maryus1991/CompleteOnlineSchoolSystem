from django.urls import path

from apps.users.students import views

app_name = 'student'

urlpatterns = [
    path('', views.main.MainStudentDashboardView.as_view(), name="main"),
    path('account/', views.main.EditAccountView.as_view(), name='account'),

    # tickets
    path('tickets/', views.ticket.TicketListView.as_view(), name='ticket-list'),
    path('tickets/create/', views.ticket.TicketCreateView.as_view(), name='ticket-create'),
    path('tickets/<int:pk>', views.ticket.TicketChatView.as_view(), name='ticket-chat'),

    # exam
    path('exam/', views.exams.ExamListView.as_view(), name='exam-list'),
    path('<int:pk>/set-exam-informations/', views.exams.SetExamInformationView.as_view(), name='exam-information'),
    path('<int:pk>/start-exam/', views.exams.StartExamView.as_view(), name='exam-start'),
    path('<int:pk>/start-exam/<int:question_id>/', views.exams.StartExamView.as_view(), name='exam-start-with-question-id'),
    path('<int:pk>/exam-answer/<int:question_id>/<int:option_id>/', views.exams.ExamSetAnswerOptions.as_view(), name='exam-set-option'),
    path('<int:pk>/set-skipped/<int:question_id>/', views.exams.ExamSetSkippedToQuestion.as_view(), name='exam-set-skipped'),
    path('<int:pk>/finished/', views.exams.ExamFinished.as_view(), name='exam-finished'),

    # reports
    path("reports/", views.reports.ExamReportListView.as_view(), name="report-list" ),
    path("reports/<int:pk>", views.reports.ExamReportDetailsView.as_view(), name="report-details" ),
    path("reports/<int:pk>/questions", views.reports.ExamReportQuestionView.as_view(), name="report-details-question" ),

    # comprehensive exam reports
    path("comprehensive/", views.reports.ComprehensiveExamListView.as_view(), name="comprehensive-list"),

]