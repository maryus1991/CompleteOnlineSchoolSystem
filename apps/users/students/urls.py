from django.urls import path

from apps.users.students import views

app_name = 'student'

urlpatterns = [
    path('', views.main.MainStudentDashboardView.as_view(), name="main"),
    path('account/', views.main.EditAccountView.as_view(), name='account'),

    path('tickets/', views.ticket.TicketListView.as_view(), name='ticket-list'),
    path('tickets/create/', views.ticket.TicketCreateView.as_view(), name='ticket-create'),
    path('tickets/<int:pk>', views.ticket.TicketChatView.as_view(), name='ticket-chat'),


    path('exam/', views.exams.ExamListView.as_view(), name='exam-list'),


]