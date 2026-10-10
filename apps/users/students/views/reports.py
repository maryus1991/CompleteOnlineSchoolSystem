from django.views.generic import ListView, View
from django.contrib import messages
from apps.reports.models import ExamReport

from apps.users.students.mixins import StudentMixin
from django.shortcuts import get_object_or_404, redirect, render

class ExamReportDetailsView(StudentMixin, View):
    template_name = "dashboard/report/detail.html"
    context_object_name = "report"


    def get(self, request, *args, **kwargs):
        obj = get_object_or_404(
            ExamReport.objects
            .select_related("exam", "exam__lesson", "exam__grade", "exam__major")
            .filter(is_active=True, student=request.student),
            pk=kwargs.get("pk"),
        )
        if obj.status != ExamReport.ReportStatus.PUBLISHED:
            messages.info(request, "کارنامه شما هنوز انتشار نیافته است")
            return redirect("student:report-list")
        return render(request, self.template_name, {"report": obj})


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
                is_active=True
            )
            .select_related("exam")
            .order_by("-sort_number", "-published_at", "-pk")
        )

    def get_context_data(self, *args, **kwargs):
        data = super().get_context_data(*args, **kwargs)
        data.update({
            "status": ExamReport.ReportStatus
        })
        return data