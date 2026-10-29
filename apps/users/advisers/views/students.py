from django.contrib import messages
from django.db.models import Prefetch, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.views.generic import ListView
from apps.categories.models import GradeCategories, MajorCategories
from apps.exams.models import Exam
from apps.practice.models import PracticeStudentDetails
from apps.progress.models import StudyPlan, DailyStudyLog, CounselingSession
from apps.reports.models import ExamReport
from apps.schools.models import School
from apps.users.advisers.forms.account import StudentCounselingProfileForm
from apps.users.advisers.mixins import AdviserMixin


class AdviserStudentListView(AdviserMixin, ListView):
    """adviser students list """
    template_name = "adviser/students/list.html"
    context_object_name = "items"
    paginate_by = 50

    def get_queryset(self):
        qs = self.get_adviser_students_queryset()

        grade_id = self.request.GET.get("grade")
        major_id = self.request.GET.get("major")
        school_id = self.request.GET.get("school")
        q = (self.request.GET.get("q") or "").strip()

        if grade_id and grade_id.isdigit():
            qs = qs.filter(grade_id=int(grade_id))
        if major_id and major_id.isdigit():
            qs = qs.filter(major_id=int(major_id))
        if school_id and school_id.isdigit():
            qs = qs.filter(school_id=int(school_id))
        if q:
            qs = qs.filter(
                Q(user__first_name__icontains=q)
                | Q(user__last_name__icontains=q)
                | Q(user__PhoneNumber__icontains=q)
                | Q(target_major_rank__icontains=q)
            )

        published_reports_qs = (
            ExamReport.objects.filter(
                is_active=True,
                status=ExamReport.ReportStatus.PUBLISHED,
            )
            .select_related("exam")
            .order_by("-published_at", "-pk")
        )
        active_plans_qs = (
            StudyPlan.objects.filter(
                is_active=True,
                status=StudyPlan.Status.ACTIVE,
            )
            .prefetch_related("items")
            .order_by("-start_date", "-pk")
        )

        return qs.prefetch_related(
            Prefetch("exam_reports", queryset=published_reports_qs, to_attr="prefetched_reports"),
            Prefetch("study_plans", queryset=active_plans_qs, to_attr="prefetched_active_plans"),
        ).order_by("-pk")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        for student in ctx["items"]:
            student.latest_report = (
                student.prefetched_reports[0] if getattr(student, "prefetched_reports", None) else None
            )
            active_plan = (
                student.prefetched_active_plans[0]
                if getattr(student, "prefetched_active_plans", None)
                else None
            )
            student.current_plan = active_plan
            student.current_plan_progress = (
                active_plan.completion_percentage() if active_plan else 0
            )

        ctx["grades"] = GradeCategories.objects.filter(is_active=True)
        ctx["majors"] = MajorCategories.objects.filter(is_active=True)
        ctx["schools"] = School.objects.filter(is_active=True)
        ctx["selected_grade"] = self.request.GET.get("grade", "")
        ctx["selected_major"] = self.request.GET.get("major", "")
        ctx["selected_school"] = self.request.GET.get("school", "")
        ctx["search_query"] = self.request.GET.get("q", "")
        return ctx


class AdviserStudent360DetailView(AdviserMixin, View):
    """full student report"""
    template_name = "adviser/students/detail_360.html"

    def get_student(self):
        return get_object_or_404(
            self.get_adviser_students_queryset(),
            pk=self.kwargs["pk"],
        )

    def _build_context(self, student, profile_form=None):
        if profile_form is None:
            profile_form = StudentCounselingProfileForm(instance=student)

        exam_reports = (
            ExamReport.objects.filter(
                student=student,
                is_active=True,
                status=ExamReport.ReportStatus.PUBLISHED,
            )
            .select_related("exam", "exam__lesson", "adviser_prescription")
            .order_by("-published_at", "-pk")
        )

        # آزمون‌های جامع دانش‌آموز
        published_reports_for_children = ExamReport.objects.filter(
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
        children_qs = (
            Exam.objects.filter(is_active=True)
            .prefetch_related(
                Prefetch(
                    "reports",
                    queryset=published_reports_for_children,
                    to_attr="student_reports",
                )
            )
            .order_by("-sort_number", "-pk")
        )
        comprehensive_exams = (
            Exam.objects.filter(
                is_active=True,
                selected_student=student,
                comprehensive_exam=True,
                parent__isnull=True,
            )
            .prefetch_related(
                Prefetch("children", queryset=children_qs, to_attr="comprehensive_children")
            )
            .order_by("-sort_number", "-pk")
            .distinct()
        )

        practice_details = (
            PracticeStudentDetails.objects.filter(
                student=student,
                is_active=True,
            )
            .select_related("practice", "question")
            .order_by("-pk")[:30]
        )

        study_plans = (
            StudyPlan.objects.filter(
                student=student,
                is_active=True,
            )
            .prefetch_related("items", "items__lesson")
            .order_by("-start_date", "-pk")
        )

        daily_logs = (
            DailyStudyLog.objects.filter(
                student=student,
                is_active=True,
            )
            .select_related("lesson", "study_plan_item")
            .order_by("-log_date", "-pk")[:30]
        )

        sessions = (
            CounselingSession.objects.filter(
                student=student,
                is_active=True,
            )
            .select_related("adviser", "adviser__user")
            .order_by("-scheduled_at", "-pk")
        )

        return {
            "student": student,
            "profile_form": profile_form,
            "exam_reports": exam_reports,
            "comprehensive_exams": comprehensive_exams,
            "practice_details": practice_details,
            "study_plans": study_plans,
            "daily_logs": daily_logs,
            "sessions": sessions,
        }

    def get(self, request, *args, **kwargs):
        student = self.get_student()
        return render(request, self.template_name, self._build_context(student))

    def post(self, request, *args, **kwargs):
        student = self.get_student()
        form = StudentCounselingProfileForm(request.POST, instance=student)
        if form.is_valid():
            form.save(update_fields=["target_major_rank", "counseling_notes_summary"])
            messages.success(request, "پرونده مشاوره‌ای دانش‌آموز با موفقیت بروزرسانی شد.")
            return redirect("adviser:student-detail", pk=student.pk)
        messages.error(request, "خطا در ثبت اطلاعات پرونده دانش‌آموز.")
        return render(request, self.template_name, self._build_context(student, profile_form=form))
