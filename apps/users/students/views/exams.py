
from apps.exams.models import Exam
from django.views.generic import ListView, View
from apps.users.students.mixins import StudentMixin


class StartExamView(StudentMixin, View):
    """for start exam by student"""

    pass

class ExamListView(StudentMixin, ListView):
    """exam list view for student dashboard"""

    template_name = 'dashboard/exam/list.html'
    context_object_name = 'items'

    def get_queryset(self):
        return self.request.student.exam.select_related("grade", "major", "lesson")

    def get_context_data(self, *args, **kwargs) :

        data = super().get_context_data(*args, **kwargs)
        data['status'] = Exam.ExamStatus
        return data