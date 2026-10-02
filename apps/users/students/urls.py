from django.urls import path

from apps.users.students import views

app_name = 'student'

urlpatterns = [
    path('', views.main.MainStudentDashboardView.as_view(), name="main"),
    path('account/', views.main.EditAccountView.as_view(), name='account'),
]