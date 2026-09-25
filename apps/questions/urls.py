
from django.urls import path

from .views import QuestionBankListView


app_name = "question"

urlpatterns = [
    path(
        "",
        QuestionBankListView.as_view(),
        name="list",
    ),
]

