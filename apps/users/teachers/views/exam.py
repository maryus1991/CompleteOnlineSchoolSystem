from django.views.generic import ListView, CreateView, UpdateView, DeleteView, View

from apps.users.teachers.mixins import TeacherMixin
from apps.exams.models import Exam
from apps.schools.models import School


class ExamListView(TeacherMixin, ListView):pass
class ExamCreateView(TeacherMixin, CreateView):pass
class ExamUpdateView(TeacherMixin, UpdateView):pass
class ExamDeleteView(TeacherMixin, DeleteView):pass

class ExamSetStudentView(TeacherMixin, View):pass