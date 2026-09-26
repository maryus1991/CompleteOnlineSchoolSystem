
from django.urls import path

from . import views


app_name = "question"

urlpatterns = [
    path("", views.QuestionBankListView.as_view(), name="list"),
    path("<int:pk>", views.QuestionBankDetailsView.as_view(), name="details"),
]

