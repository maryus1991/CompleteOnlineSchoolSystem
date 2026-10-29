from django.urls import path
from . import views

app_name = "adviser"

urlpatterns = [
    path("", views.main.AdviserDashboardView.as_view(), name="main"),
    path("account/", views.main.EditAdviserAccountView.as_view(), name="account"),

    # students 360
    path("students/", views.students.AdviserStudentListView.as_view(), name="student-list"),
    path("students/<int:pk>/", views.students.AdviserStudent360DetailView.as_view(), name="student-detail"),

    # study plans & weekly items
    path("plans/", views.study_plan.StudyPlanListView.as_view(), name="plan-list"),
    path("plans/create/", views.study_plan.StudyPlanCreateView.as_view(), name="plan-create"),
    path("plans/<int:pk>/update/", views.study_plan.StudyPlanUpdateView.as_view(), name="plan-update"),
    path("plans/<int:pk>/delete/", views.study_plan.StudyPlanDeleteView.as_view(), name="plan-delete"),
    path("plans/<int:pk>/items/", views.study_plan.StudyPlanItemsManageView.as_view(), name="plan-items"),

    # daily study logs
    path("daily-logs/", views.study_plan.DailyLogReviewListView.as_view(), name="daily-log-list"),
    path("daily-logs/<int:pk>/review/", views.study_plan.DailyLogReviewActionView.as_view(), name="daily-log-review"),

    # exam reports & prescriptions
    path("reports/", views.reports.AdviserStudentExamReportListView.as_view(), name="report-list"),
    path("reports/<int:report_pk>/questions/", views.reports.AdviserExamQuestionAnalysisView.as_view(), name="report-questions"),
    path("reports/<int:report_pk>/prescription/", views.reports.AdviserExamPrescriptionCreateOrUpdateView.as_view(), name="prescription-create"),

    # counseling sessions & site requests
    path("sessions/", views.sessions.CounselingSessionListView.as_view(), name="session-list"),
    path("sessions/create/", views.sessions.CounselingSessionCreateView.as_view(), name="session-create"),
    path("sessions/<int:pk>/update/", views.sessions.CounselingSessionUpdateView.as_view(), name="session-update"),
    path("site-requests/", views.sessions.SiteCounselingRequestListView.as_view(), name="site-requests"),
    path("site-requests/<int:pk>/update/", views.sessions.SiteCounselingRequestUpdateView.as_view(), name="site-request-update"),

    # tickets
    path("tickets/", views.ticket.TicketListView.as_view(), name="ticket-list"),
    path("tickets/create/", views.ticket.TicketCreateView.as_view(), name="ticket-create"),
    path("tickets/<int:pk>/", views.ticket.TicketChatView.as_view(), name="ticket-chat"),
]
