from apps.users.teachers.mixins import TeacherMixin
from apps.users.teachers.models import Teacher
from django.views.generic import CreateView, ListView, UpdateView, RedirectView
from apps.article.models import Article


class ArticleCreateView(TeacherMixin, CreateView):
    """article create view for teacher"""

class ArticleUpdateView(TeacherMixin, UpdateView):
    """article update view for teacher"""

class ArticleDeleteView(TeacherMixin, RedirectView):
    """article  delete view for teacher"""

class ArticleListView(TeacherMixin, ListView):
    """article list view for teacher """
