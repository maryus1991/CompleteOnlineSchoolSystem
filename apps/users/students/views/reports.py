from django.views.generic import ListView

from apps.reports.models import ExamReport
from apps.users.students.mixins import StudentMixin


class ExamReportListView(StudentMixin, ListView):
    model = ExamReport
    template_name = "dashboard/report/list.html"
    context_object_name = "items"
    paginate_by = 100

    def get_queryset(self):
        return (
            ExamReport.objects
            .filter(
                student=self.request.student,
            )
            .select_related("exam")
            .order_by("-sort_number", "-published_at", "-pk")
        )