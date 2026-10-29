from django.views.generic import ListView, View, DetailView
from django.contrib import messages
from apps.reports.models import ExamReport, Exam
from apps.questions.models import StudentAnswer
from apps.users.students.mixins import StudentMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Sum, Count, Q, Prefetch
import json
from django.core.serializers.json import DjangoJSONEncoder


class ComprehensiveExamAnalysisView(StudentMixin, DetailView):
    model = Exam
    template_name = "dashboard/report/comprehensive-analysis.html"
    context_object_name = "exam"

    def get_queryset(self):
        student = self.request.student

        published_reports = (
            ExamReport.objects.filter(
                student=student,
                status=ExamReport.ReportStatus.PUBLISHED,
            )
            .only(
                "id",
                "exam_id",
                "student_id",
                "score",
                "max_score",
                "percentage",
                "answered_percentage",
                "rank",
                "teraze",
                "total_questions",
                "correct_count",
                "wrong_count",
                "unanswered_count",
                "skipped_count",
                "uncorrected_count",
                "calculated_at",
                "published_at",
            )
        )

        children = (
            Exam.objects.filter(is_active=True)
            .prefetch_related(
                Prefetch(
                    "reports",
                    queryset=published_reports,
                    to_attr="student_reports",
                )
            )
            .only(
                "id",
                "name",
                "parent_id",
                "sort_number",
                "max_score",
                "start_at",
            )
            .order_by("start_at", "pk")
        )

        return (
            Exam.objects.filter(
                is_active=True,
                selected_student=student,
                comprehensive_exam=True,
                parent__isnull=True,
            )
            .prefetch_related(
                Prefetch(
                    "children",
                    queryset=children,
                    to_attr="analysis_children",
                )
            )
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        exam = self.object

        children = exam.analysis_children
        reports = []

        for child in children:
            child_reports = child.student_reports
            report = child_reports[0] if child_reports else None

            child.analysis_report = report

            if report:
                reports.append((child, report))

        report_objects = [report for _, report in reports]
        percentages = [r.percentage for r in report_objects]
        terazes = [
            r.teraze for r in report_objects
            if r.teraze is not None
        ]

        def average(values):
            return round(sum(values) / len(values), 1) if values else None

        total_questions = sum(
            r.total_questions for r in report_objects
        )
        correct = sum(r.correct_count for r in report_objects)
        wrong = sum(r.wrong_count for r in report_objects)
        unanswered = sum(r.unanswered_count for r in report_objects)
        skipped = sum(r.skipped_count for r in report_objects)
        uncorrected = sum(r.uncorrected_count for r in report_objects)

        answered = correct + wrong
        average_percentage = average(percentages)

        # رتبه کمتر به معنی جایگاه بهتر است.
        ranked_reports = [
            (child, report)
            for child, report in reports
            if report.rank is not None
        ]

        best_result = max(
            reports,
            key=lambda item: item[1].percentage,
            default=None,
        )
        weakest_result = min(
            reports,
            key=lambda item: item[1].percentage,
            default=None,
        )

        def chart_data(value):
            return json.dumps(
                value,
                cls=DjangoJSONEncoder,
                ensure_ascii=False,
            )

        context.update({
            "children": children,
            "reports": report_objects,
            "report_count": len(report_objects),
            "child_count": len(children),
            "average_percentage": average_percentage,
            "average_teraze": average(terazes),
            "average_rank": average([
                r.rank for r in report_objects
                if r.rank is not None
            ]),
            "total_questions": total_questions,
            "correct_count": correct,
            "wrong_count": wrong,
            "unanswered_count": unanswered,
            "skipped_count": skipped,
            "uncorrected_count": uncorrected,
            "answered_count": answered,
            "overall_answered_percentage": (
                round(answered * 100 / total_questions, 1)
                if total_questions else 0
            ),
            "best_result": best_result,
            "weakest_result": weakest_result,
            "ranked_count": len(ranked_reports),

            "chart_labels": chart_data([
                child.name for child, report in reports
            ]),
            "chart_percentages": chart_data([
                report.percentage for child, report in reports
            ]),
            "chart_scores": chart_data([
                report.score for child, report in reports
            ]),
            "chart_max_scores": chart_data([
                report.max_score for child, report in reports
            ]),
            "chart_terazes": chart_data([
                report.teraze for child, report in reports
            ]),
            "chart_ranks": chart_data([
                report.rank for child, report in reports
            ]),
            "chart_answered_percentages": chart_data([
                report.answered_percentage for child, report in reports
            ]),
            "chart_answer_distribution": chart_data([
                correct, wrong, unanswered, skipped, uncorrected
            ]),
        })

        return context



class ComprehensiveExamListView(StudentMixin, ListView):

    template_name = "dashboard/report/comprehensive_exam_list.html"
    context_object_name = "comprehensive_exams"

    def get_queryset(self):
        student = self.request.student

        published_reports = ExamReport.objects.filter(
            student=student,
            status=ExamReport.ReportStatus.PUBLISHED,
        ).only(
            "id",
            "exam_id",
            "student_id",
            "score",
            "max_score",
            "percentage",
            "answered_percentage",
            "rank",
            "teraze",
            "status",
        )

        children_queryset = (
            Exam.objects.filter(is_active=True)
            .prefetch_related(
                Prefetch(
                    "reports",
                    queryset=published_reports,
                    to_attr="student_reports",
                )
            )
            .only(
                "id",
                "name",
                "parent_id",
                "start_at",
                "stop_at",
                "max_score",
                "sort_number",
            )
            .order_by("-sort_number", "-pk")
        )

        return (
            Exam.objects.filter(
                is_active=True,
                selected_student=student,
                comprehensive_exam=True,
                parent__isnull=True,
            )
            .prefetch_related(
                Prefetch(
                    "children",
                    queryset=children_queryset,
                    to_attr="comprehensive_children",
                )
            )
            .order_by("-sort_number", "-pk")
            .distinct()
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        for exam in context["comprehensive_exams"]:
            reports = [
                child.student_reports[0]
                for child in exam.comprehensive_children
                if child.student_reports
            ]

            exam.comparison = {
                "total": len(exam.comprehensive_children),
                "published": len(reports),
                "average_percentage": (
                    round(
                        sum(report.percentage for report in reports)
                        / len(reports),
                        1,
                    )
                    if reports
                    else None
                ),
                "average_teraze": (
                    round(
                        sum(
                            report.teraze
                            for report in reports
                            if report.teraze is not None
                        )
                        / len([
                            report for report in reports
                            if report.teraze is not None
                        ]),
                        1,
                    )
                    if any(
                        report.teraze is not None
                        for report in reports
                    )
                    else None
                ),
            }

        return context


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
            .select_related(
                "exam",
                "exam__lesson",
                "exam__grade",
                "exam__major",
                "adviser_prescription",
                "adviser_prescription__adviser",
                "adviser_prescription__adviser__user",
            )
            .filter(is_active=True, student=request.student),
            pk=kwargs.get("pk"),
        )
        if obj.status != ExamReport.ReportStatus.PUBLISHED:
            messages.info(request, "کارنامه شما هنوز انتشار نیافته است")
            return redirect("student:report-list")

        prescription = getattr(obj, "adviser_prescription", None)
        if prescription and not prescription.is_seen_by_student:
            prescription.is_seen_by_student = True
            prescription.save(update_fields=["is_seen_by_student"])

        return render(
            request,
            self.template_name,
            {
                "report": obj,
                "prescription": prescription,
            },
        )


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
            .select_related("exam", "adviser_prescription")
            .order_by("-sort_number", "-published_at", "-pk")
        )

    def get_context_data(self, *args, **kwargs):
        data = super().get_context_data(*args, **kwargs)
        data.update({
            "status": ExamReport.ReportStatus
        })
        return data
