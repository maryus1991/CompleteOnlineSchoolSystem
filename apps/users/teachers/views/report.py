from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import DeleteView, ListView, UpdateView

from apps.exams.models import Exam
from apps.reports.models import ExamReport
from apps.users.teachers.forms.report import ExamReportForm
from apps.users.teachers.mixins import TeacherMixin


def _teacher_exams(teacher):
    return Exam.objects.filter(teacher=teacher, is_active=True)


class ReportExamListView(TeacherMixin, ListView):
    """لیست آزمون‌هایی که معلم دارد (برای ورود به کارنامه‌ها)"""

    permission_field = "can_add_exam"
    template_name = "teacher/report/exam_list.html"
    context_object_name = "items"
    paginate_by = 50

    def get_queryset(self):
        return (
            _teacher_exams(self.request.teacher)
            .select_related("grade", "major", "lesson")
            .order_by("-pk")
        )


class ReportListView(TeacherMixin, ListView):
    """لیست کارنامه‌های یک آزمون خاص"""

    permission_field = "can_add_exam"
    template_name = "teacher/report/list.html"
    context_object_name = "items"
    paginate_by = 50

    def get_exam(self):
        return get_object_or_404(
            _teacher_exams(self.request.teacher),
            pk=self.kwargs["exam_pk"],
        )

    def get_queryset(self):
        self.exam = self.get_exam()
        return (
            ExamReport.objects
            .filter(exam=self.exam)
            .select_related("student", "student__user", "exam")
            .order_by("rank", "-score", "pk")
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["exam"] = self.exam
        return ctx


class ReportUpdateView(TeacherMixin, UpdateView):
    """ویرایش کارنامه — exam و student قابل تغییر نیستند"""

    permission_field = "can_add_exam"
    model = ExamReport
    form_class = ExamReportForm
    template_name = "teacher/report/form.html"
    context_object_name = "report"

    def get_queryset(self):
        return (
            ExamReport.objects
            .filter(exam__teacher=self.request.teacher, exam__is_active=True)
            .select_related("exam", "student", "student__user")
        )

    def get_success_url(self):
        return reverse(
            "teacher:report-list",
            kwargs={"exam_pk": self.object.exam_id},
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["page_title"] = "ویرایش کارنامه"
        ctx["page_subtitle"] = (
            f"{self.object.exam.name} — {self.object.student}"
        )
        ctx["exam"] = self.object.exam
        return ctx

    def form_valid(self, form):
        # تضمین: exam و student عوض نشوند
        form.instance.exam_id = self.get_object().exam_id
        form.instance.student_id = self.get_object().student_id
        messages.success(self.request, "کارنامه با موفقیت بروزرسانی شد.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, form.errors)
        return self.render_to_response(self.get_context_data(form=form))


class ReportDeleteView(TeacherMixin, DeleteView):
    """حذف کارنامه یک دانش‌آموز"""

    permission_field = "can_add_exam"
    model = ExamReport
    template_name = "teacher/report/confirm_delete.html"
    context_object_name = "report"

    def get_queryset(self):
        return ExamReport.objects.filter(
            exam__teacher=self.request.teacher,
            exam__is_active=True,
        ).select_related("exam", "student", "student__user")

    def get_success_url(self):
        return reverse(
            "teacher:report-list",
            kwargs={"exam_pk": self.object.exam_id},
        )

    def form_valid(self, form):
        exam_id = self.object.exam_id
        self.object.delete()
        messages.success(self.request, "کارنامه حذف شد.")
        return HttpResponseRedirect(
            reverse("teacher:report-list", kwargs={"exam_pk": exam_id})
        )