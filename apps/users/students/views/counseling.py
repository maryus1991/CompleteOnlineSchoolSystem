from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from apps.common.utils import datetime2jalali
from django.views import View
from django.views.generic import DetailView, ListView, TemplateView

from apps.live_classes.models import AdviserLiveSession
from apps.progress.models import (
    StudyPlan,
    StudyPlanItem,
    DailyStudyLog,
    AdviserExamPrescription,
    CounselingSession,
)
from apps.reports.models import ExamReport
from apps.users.students.forms.counseling import (
    StudentDailyStudyLogForm,
    StudentSessionRequestForm,
    StudentPrescriptionReflectionForm,
)
from apps.users.students.mixins import StudentMixin


def _get_student_adviser_live_sessions_qs(student):

    if not student or not student.adviser:


        return AdviserLiveSession.objects.none()


    return (
        AdviserLiveSession.objects.filter(
            is_active=True,
            adviser_id=student.adviser.id,
            adviser__is_active=True,
            server__is_active=True,
        )
        .filter(
            Q(students=student)
            | Q(counseling_session__student=student)
            | Q(students__isnull=True, counseling_session__isnull=True)
        )
        .select_related(
            "adviser",
            "adviser__user",
            "adviser__school",
            "counseling_session",
            "server",
        )
        .prefetch_related("report")
        .distinct()
        .order_by("-pk")
    )


class StudentCounselingHubView(StudentMixin, TemplateView):
    """Counseling Dashboard in the Student Panel"""
    template_name = "dashboard/counseling/hub.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        student = self.request.student

        active_plan = (
            StudyPlan.objects.filter(
                student=student,
                is_active=True,
                status=StudyPlan.Status.ACTIVE,
            )
            .select_related("adviser", "adviser__user")
            .prefetch_related("items", "items__lesson")
            .order_by("-start_date", "-pk")
            .first()
        )

        all_plans = (
            StudyPlan.objects.filter(student=student, is_active=True)
            .select_related("adviser", "adviser__user")
            .prefetch_related("items")
            .order_by("-start_date", "-pk")[:6]
        )

        upcoming_sessions = (
            CounselingSession.objects.filter(
                student=student,
                is_active=True,
            )
            .select_related("adviser", "adviser__user")
            .order_by("-scheduled_at", "-pk")[:6]
        )

        live_sessions = list(_get_student_adviser_live_sessions_qs(student)[:6])
        for item in live_sessions:
            item.report_obj = next(
                (r for r in item.report.all() if r.is_active),
                None,
            )

        prescriptions = (
            AdviserExamPrescription.objects.filter(
                student=student,
                is_active=True,
            )
            .select_related(
                "exam_report",
                "exam_report__exam",
                "adviser",
                "adviser__user",
            )
            .order_by("-created_at", "-pk")[:6]
        )

        recent_logs = (
            DailyStudyLog.objects.filter(
                student=student,
                is_active=True,
            )
            .select_related("lesson", "study_plan_item")
            .order_by("-log_date", "-pk")[:6]
        )

        ctx.update(
            {
                "student": student,
                "adviser": student.adviser,
                "active_plan": active_plan,
                "active_plan_progress": active_plan.completion_percentage() if active_plan else 0,
                "all_plans": all_plans,
                "upcoming_sessions": upcoming_sessions,
                "live_sessions": live_sessions,
                "prescriptions": prescriptions,
                "recent_logs": recent_logs,
            }
        )
        return ctx


class StudentStudyPlanListView(StudentMixin, ListView):
    """student weakly study plan list """
    template_name = "dashboard/counseling/plan_list.html"
    context_object_name = "items"
    paginate_by = 30

    def get_queryset(self):
        return (
            StudyPlan.objects.filter(
                student=self.request.student,
                is_active=True,
            )
            .select_related("adviser", "adviser__user")
            .prefetch_related("items")
            .order_by("-start_date", "-pk")
        )


class StudentStudyPlanDetailView(StudentMixin, View):
    """Display of the student's weekly schedule (Saturday to Friday) and the completion status of the tasks (boxes)."""
    template_name = "dashboard/counseling/plan_detail.html"

    def get(self, request, *args, **kwargs):
        plan = get_object_or_404(
            StudyPlan.objects.filter(
                student=request.student,
                is_active=True,
            )
            .select_related("adviser", "adviser__user")
            .prefetch_related("items", "items__lesson"),
            pk=kwargs["pk"],
        )

        grouped = {
            day_val: {"label": day_label, "items": []}
            for day_val, day_label in StudyPlanItem.DayOfWeek.choices
        }
        for item in plan.items.filter(is_active=True).select_related("lesson").order_by("day_of_week", "sort_number", "pk"):
            if item.day_of_week in grouped:
                grouped[item.day_of_week]["items"].append(item)

        return render(
            request,
            self.template_name,
            {
                "plan": plan,
                "days_grouped": grouped,
                "completion_percentage": plan.completion_percentage(),
            },
        )


class StudentTogglePlanItemView(StudentMixin, View):
    """Checking or unchecking the completion of a study task by the student"""

    def post(self, request, *args, **kwargs):
        item = get_object_or_404(
            StudyPlanItem.objects.filter(
                study_plan__student=request.student,
                study_plan__is_active=True,
                is_active=True,
            ).select_related("study_plan"),
            pk=kwargs["item_pk"],
        )
        item.is_completed_by_student = not item.is_completed_by_student
        item.completed_at = datetime2jalali() if item.is_completed_by_student else None
        item.save(update_fields=["is_completed_by_student", "completed_at"])

        if item.is_completed_by_student:
            messages.success(
                request,
                f"باکس «{item.topic}» انجام شد. پیشرفت برنامه: {item.study_plan.completion_percentage()}٪",
            )
        else:
            messages.info(request, f"وضعیت باکس «{item.topic}» به انجام‌نشده تغییر یافت.")

        next_url = request.POST.get("next") or reverse(
            "student:counseling-plan-detail", kwargs={"pk": item.study_plan_id}
        )
        return redirect(next_url)


class StudentDailyLogListCreateView(StudentMixin, View):
    """Student Daily Work Log Form + Log History and Counselor Feedback"""
    template_name = "dashboard/counseling/daily_logs.html"

    def _get_logs(self, student):
        return (
            DailyStudyLog.objects.filter(
                student=student,
                is_active=True,
            )
            .select_related("lesson", "study_plan_item", "study_plan_item__study_plan")
            .order_by("-log_date", "-pk")
        )

    def get(self, request, *args, **kwargs):
        form = StudentDailyStudyLogForm(student=request.student)
        return render(
            request,
            self.template_name,
            {
                "form": form,
                "items": self._get_logs(request.student),
            },
        )

    def post(self, request, *args, **kwargs):
        form = StudentDailyStudyLogForm(
            request.POST,
            request.FILES,
            student=request.student,
        )
        if form.is_valid():
            log_obj = form.save(commit=False)
            log_obj.student = request.student
            log_obj.review_status = DailyStudyLog.ReviewStatus.PENDING
            log_obj.save()

            # اگر آیتم برنامه انتخاب شده بود، آن را تکمیل‌شده علامت بزن
            if log_obj.study_plan_item and not log_obj.study_plan_item.is_completed_by_student:
                log_obj.study_plan_item.is_completed_by_student = True
                log_obj.study_plan_item.completed_at = datetime2jalali()
                log_obj.study_plan_item.save(
                    update_fields=["is_completed_by_student", "completed_at"]
                )

            messages.success(
                request,
                "گزارش کار روزانه شما با موفقیت ثبت شد و برای بررسی مشاور ارسال گردید.",
            )
            return redirect("student:counseling-daily-logs")

        messages.error(request, "لطفاً اطلاعات واردشده در فرم گزارش کار را بررسی کنید.")
        messages.error(request, form.errors.as_ul())
        return render(
            request,
            self.template_name,
            {
                "form": form,
                "items": self._get_logs(request.student),
            },
        )


class StudentExamPrescriptionDetailView(StudentMixin, View):
    """Displaying the counselor’s specialized version on the exam report + recording the student’s commitment"""
    template_name = "dashboard/counseling/prescription_detail.html"

    def get_report_and_prescription(self, request, report_pk):
        report = get_object_or_404(
            ExamReport.objects.filter(
                student=request.student,
                is_active=True,
            ).select_related("exam", "exam__lesson", "adviser_prescription", "adviser_prescription__adviser", "adviser_prescription__adviser__user"),
            pk=report_pk,
        )
        prescription = get_object_or_404(
            AdviserExamPrescription.objects.select_related("adviser", "adviser__user"),
            exam_report=report,
            student=request.student,
            is_active=True,
        )
        return report, prescription

    def get(self, request, *args, **kwargs):
        report, prescription = self.get_report_and_prescription(request, kwargs["report_pk"])
        if not prescription.is_seen_by_student:
            prescription.is_seen_by_student = True
            prescription.save(update_fields=["is_seen_by_student"])

        form = StudentPrescriptionReflectionForm(instance=prescription)
        return render(
            request,
            self.template_name,
            {
                "report": report,
                "prescription": prescription,
                "form": form,
            },
        )

    def post(self, request, *args, **kwargs):
        report, prescription = self.get_report_and_prescription(request, kwargs["report_pk"])
        form = StudentPrescriptionReflectionForm(request.POST, instance=prescription)
        if form.is_valid():
            updated = form.save(commit=False)
            updated.is_seen_by_student = True
            updated.save(update_fields=["student_reflection", "is_seen_by_student"])
            messages.success(request, "پاسخ و تعهد شما برای آزمون بعدی ثبت شد.")
            next_url = request.POST.get("next") or reverse(
                "student:counseling-prescription-detail", kwargs={"report_pk": report.pk}
            )
            return redirect(next_url)

        messages.error(request, "خطا در ثبت پاسخ شما.")
        return render(
            request,
            self.template_name,
            {
                "report": report,
                "prescription": prescription,
                "form": form,
            },
        )


class StudentSessionListRequestView(StudentMixin, View):
    """Viewing counseling sessions and requesting an additional session by the student"""
    template_name = "dashboard/counseling/sessions.html"

    def _get_sessions(self, student):
        return (
            CounselingSession.objects.filter(
                student=student,
                is_active=True,
            )
            .select_related("adviser", "adviser__user")
            .order_by("-scheduled_at", "-pk")
        )

    def _get_live_sessions(self, student):
        qs = list(_get_student_adviser_live_sessions_qs(student)[:10])
        for item in qs:
            item.report_obj = next(
                (r for r in item.report.all() if r.is_active),
                None,
            )
        return qs

    def get(self, request, *args, **kwargs):
        form = StudentSessionRequestForm()
        return render(
            request,
            self.template_name,
            {
                "form": form,
                "items": self._get_sessions(request.student),
                "live_sessions": self._get_live_sessions(request.student),
                "adviser": request.student.adviser,
            },
        )

    def post(self, request, *args, **kwargs):
        student = request.student
        if not student.adviser:
            messages.warning(
                request,
                "هنوز مشاور اختصاصی برای حساب شما تعیین نشده است. لطفاً با پشتیبانی تماس بگیرید.",
            )
            return redirect("student:counseling-sessions")

        form = StudentSessionRequestForm(request.POST)
        if form.is_valid():
            session_obj = form.save(commit=False)
            session_obj.student = student
            session_obj.adviser = student.adviser
            session_obj.status = CounselingSession.Status.REQUESTED_BY_STUDENT
            session_obj.save()
            messages.success(
                request,
                "درخواست جلسه مشاوره شما ثبت شد و پس از تایید مشاور زمان نهایی اعلام می‌گردد.",
            )
            return redirect("student:counseling-sessions")

        messages.error(request, "لطفاً اطلاعات درخواست جلسه را بررسی کنید.")
        return render(
            request,
            self.template_name,
            {
                "form": form,
                "items": self._get_sessions(student),
                "live_sessions": self._get_live_sessions(student),
                "adviser": student.adviser,
            },
        )


class StudentAdviserLiveSessionListView(StudentMixin, ListView):
    """
    فهرست جلسات آنلاین مشاوره دانش‌آموز با مشاور اختصاصی خود.
    دانش‌آموز فقط جلساتی را می‌بیند که مشاور خودش برگزارکننده آن است و دانش‌آموز مجاز به حضور در آن است.
    """
    model = AdviserLiveSession
    template_name = "dashboard/counseling/live_list.html"
    context_object_name = "live_sessions"
    paginate_by = 24

    def get_queryset(self):
        qs = _get_student_adviser_live_sessions_qs(self.request.student)
        for item in qs:
            item.report_obj = next(
                (r for r in item.report.all() if r.is_active),
                None,
            )
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["student"] = self.request.student
        context["adviser"] = self.request.student.adviser
        return context


class StudentAdviserLiveSessionDetailView(StudentMixin, DetailView):
    """
    جزئیات یک جلسه آنلاین مشاوره برای دانش‌آموز.
    لینک ورود تنها زمانی ساخته می‌شود که جلسه در وضعیت LIVE (در حال برگزاری) باشد.
    """
    model = AdviserLiveSession
    template_name = "dashboard/counseling/live_detail.html"
    context_object_name = "live_session"
    pk_url_kwarg = "pk"

    def get_queryset(self):
        return _get_student_adviser_live_sessions_qs(self.request.student)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        live_session = self.object
        context["student"] = self.request.student
        context["adviser"] = self.request.student.adviser
        context["meeting_url"] = (
            live_session.get_student_meeting_url(self.request.user)
            if live_session.is_available
            else None
        )
        context["reports"] = live_session.report.filter(is_active=True).order_by("-pk")
        return context
