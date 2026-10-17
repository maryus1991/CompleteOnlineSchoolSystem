from django.views.generic import ListView, CreateView, UpdateView, DeleteView, View

from apps.users.teachers.mixins import TeacherMixin
from apps.questions.models import Question

class QuestionListView(TeacherMixin, ListView):
    """teacher for listing questions"""

    permission_field = "can_add_question"
    template_name = ""
    context_object_name = "items"

    def get_queryset(self):
        return Question.objects.filter(teacher=self.teacher, is_active=True)


class QuestionCreateView(TeacherMixin, CreateView):
    """teacher for create questions"""

    permission_field = "can_add_question"
    template_name = ""




class QuestionUpdateView(TeacherMixin, UpdateView):
    """teacher for update questions"""
    permission_field = "can_add_question"


class QuestionDeleteView(TeacherMixin, DeleteView):
    """teacher delete questions"""
    permission_field = "can_add_question"


