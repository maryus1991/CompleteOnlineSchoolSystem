from django.views.generic import ListView, View
from django.contrib import messages
from apps.reports.models import ExamReport, Exam
from apps.questions.models import StudentAnswer
from apps.users.students.mixins import StudentMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Sum, Count, Q


class ExamReportQuestionView(StudentMixin, View):
    template_name = "dashboard/report/questions.html"

    def get(self, request, *args, **kwargs):
        exam = get_object_or_404(
            Exam.objects.only("pk", "status", "name"),
            pk=kwargs["pk"],
            status=Exam.ExamStatus.RESULTS_PUBLISHED,
        )

        items = (
            StudentAnswer.objects.filter(
                exam=exam,
                student=request.student,
            )
            .select_related(
                "question",
                "question__answer_key",
                "selected_option",
                "corrected_by",
            )
            .prefetch_related(
                "question__options",
            )
            .order_by("question_id", "pk")
        )

        stats = items.aggregate(
            total_score=Sum("score"),
            uncorrected_count=Count(
                "pk",
                filter=Q(
                    corrected=StudentAnswer.TypeOfCorrect.not_corrected
                ),
            ),
        )

        context = {
            "items": items,
            "exam": exam,
            "total_score": stats["total_score"] or 0,
            "uncorrected_count": stats["uncorrected_count"] or 0,
        }

        return render(request, self.template_name, context)


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