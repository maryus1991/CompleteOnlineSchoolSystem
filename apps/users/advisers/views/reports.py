from django.contrib import messages
from django.db.models import Count, Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.views.generic import ListView
from apps.progress.models import AdviserExamPrescription
from apps.questions.models import StudentAnswer
from apps.reports.models import ExamReport
from apps.users.advisers.forms.prescription import AdviserExamPrescriptionForm
from apps.users.advisers.mixins import AdviserMixin


class AdviserStudentExamReportListView(AdviserMixin, ListView):
    """student report list view"""
    permission_field = "can_view_student_reports"
    template_name = "adviser/reports/list.html"
    context_object_name = "items"
    paginate_by = 50

    def get_queryset(self):
        qs = (
            ExamReport.objects.filter(
                student__in=self.get_adviser_students_queryset(),
                is_active=True,
                status=ExamReport.ReportStatus.PUBLISHED,
            )
            .select_related(
                "exam",
                "exam__grade",
                "exam__major",
                "exam__lesson",
                "student",
                "student__user",
                "adviser_prescription",
            )
            .order_by("-published_at", "-pk")
        )
        student_id = self.request.GET.get("student")
        has_prescription = self.request.GET.get("has_prescription")
        if student_id and student_id.isdigit():
            qs = qs.filter(student_id=int(student_id))
        if has_prescription == "yes":
            qs = qs.filter(adviser_prescription__isnull=False)
        elif has_prescription == "no":
            qs = qs.filter(adviser_prescription__isnull=True)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["students"] = self.get_adviser_students_queryset()
        ctx["selected_student"] = self.request.GET.get("student", "")
        ctx["selected_has_prescription"] = self.request.GET.get("has_prescription", "")
        return ctx


class AdviserExamQuestionAnalysisView(AdviserMixin, View):
    """analyze the student answers in reports"""
    permission_field = "can_view_student_reports"
    template_name = "adviser/reports/questions_analysis.html"

    def get(self, request, *args, **kwargs):
        report = get_object_or_404(
            ExamReport.objects.filter(
                student__in=self.get_adviser_students_queryset(),
                is_active=True,
            ).select_related("exam", "student", "student__user", "adviser_prescription"),
            pk=kwargs["report_pk"],
        )
        answers = (
            StudentAnswer.objects.filter(
                exam=report.exam,
                student=report.student,
            )
            .select_related(
                "question",
                "question__answer_key",
                "selected_option",
                "corrected_by",
            )
            .prefetch_related("question__options")
            .order_by("question_id", "pk")
        )
        stats = answers.aggregate(
            total_score=Sum("score"),
            uncorrected_count=Count(
                "pk",
                filter=Q(corrected=StudentAnswer.TypeOfCorrect.not_corrected),
            ),
        )
        return render(
            request,
            self.template_name,
            {
                "report": report,
                "exam": report.exam,
                "student": report.student,
                "items": answers,
                "total_score": stats["total_score"] or 0,
                "uncorrected_count": stats["uncorrected_count"] or 0,
            },
        )


class AdviserExamPrescriptionCreateOrUpdateView(AdviserMixin, View):
    """create or update a prescription for each report of student"""
    permission_field = "can_send_adviser_notes"
    template_name = "adviser/reports/prescription_form.html"

    def get_report(self):
        return get_object_or_404(
            ExamReport.objects.filter(
                student__in=self.get_adviser_students_queryset(),
                is_active=True,
            ).select_related("exam", "exam__lesson", "student", "student__user"),
            pk=self.kwargs["report_pk"],
        )

    def get(self, request, *args, **kwargs):
        report = self.get_report()
        prescription = AdviserExamPrescription.objects.filter(exam_report=report).first()
        form = AdviserExamPrescriptionForm(instance=prescription)
        return render(
            request,
            self.template_name,
            {
                "report": report,
                "prescription": prescription,
                "form": form,
                "is_update": prescription is not None,
            },
        )

    def post(self, request, *args, **kwargs):
        report = self.get_report()
        prescription = AdviserExamPrescription.objects.filter(exam_report=report).first()
        form = AdviserExamPrescriptionForm(
            request.POST,
            request.FILES,
            instance=prescription,
        )
        if form.is_valid():
            obj = form.save(commit=False)
            obj.exam_report = report
            obj.adviser = request.adviser
            obj.student = report.student
            obj.save()
            messages.success(request, "نسخه و تحلیل تخصصی کارنامه با موفقیت ثبت شد.")
            return redirect("adviser:report-list")

        messages.error(request, "لطفاً اطلاعات نسخه کارنامه را بررسی کنید.")
        return render(
            request,
            self.template_name,
            {
                "report": report,
                "prescription": prescription,
                "form": form,
                "is_update": prescription is not None,
            },
        )
