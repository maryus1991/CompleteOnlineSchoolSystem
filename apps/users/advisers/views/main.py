from datetime import timedelta
from django.contrib import messages
from django.db import transaction
from django.db.models import Count, Q
from django.shortcuts import redirect
from apps.common.utils import datetime2jalali
from django.views.generic import TemplateView
from apps.progress.models import (
    StudyPlan,
    DailyStudyLog,
    CounselingSession,
)
from apps.reports.models import ExamReport
from apps.users.advisers.forms.account import AdviserAccountForm
from apps.users.advisers.mixins import AdviserMixin
from apps.users.advisers.models import Adviser


class AdviserDashboardView(AdviserMixin, TemplateView):
    """adviser dashboard"""
    template_name = "adviser/main.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        adviser = self.request.adviser
        students_qs = self.get_adviser_students_queryset()

        students_count = students_qs.count()
        remaining_capacity = max(0, adviser.max_students_capacity - students_count)

        pending_logs_qs = (
            DailyStudyLog.objects.filter(
                student__in=students_qs,
                is_active=True,
                review_status=DailyStudyLog.ReviewStatus.PENDING,
            )
            .select_related("student", "student__user", "lesson", "study_plan_item")
            .order_by("-log_date", "-pk")
        )
        pending_logs_count = pending_logs_qs.count()
        pending_logs = pending_logs_qs[:10]

        upcoming_sessions_qs = (
            CounselingSession.objects.filter(
                adviser=adviser,
                student__in=students_qs,
                is_active=True,
                status__in=[
                    CounselingSession.Status.REQUESTED_BY_STUDENT,
                    CounselingSession.Status.SCHEDULED,
                ],
            )
            .select_related("student", "student__user")
            .order_by("scheduled_at", "-pk")
        )
        upcoming_sessions_count = upcoming_sessions_qs.count()
        upcoming_sessions = upcoming_sessions_qs[:8]

        active_plans = (
            StudyPlan.objects.filter(
                student__in=students_qs,
                is_active=True,
                status=StudyPlan.Status.ACTIVE,
            )
            .annotate(
                total_items=Count("items", filter=Q(items__is_active=True)),
                completed_items=Count(
                    "items",
                    filter=Q(items__is_active=True, items__is_completed_by_student=True),
                ),
            )
        )
        plan_percentages = [
            round((p.completed_items / p.total_items) * 100)
            for p in active_plans
            if p.total_items > 0
        ]
        average_plan_completion = (
            round(sum(plan_percentages) / len(plan_percentages))
            if plan_percentages
            else 0
        )

        three_days_ago = datetime2jalali() - timedelta(days=3)
        recent_active_student_ids = set(
            DailyStudyLog.objects.filter(
                student__in=students_qs,
                is_active=True,
                created_at__gte=three_days_ago,
            ).values_list("student_id", flat=True)
        )

        published_reports = (
            ExamReport.objects.filter(
                student__in=students_qs,
                is_active=True,
                status=ExamReport.ReportStatus.PUBLISHED,
            )
            .select_related("exam", "student", "student__user")
            .order_by("student_id", "-published_at", "-pk")
        )
        reports_by_student = {}
        for rep in published_reports:
            reports_by_student.setdefault(rep.student_id, []).append(rep)

        risk_alerts = []
        for student in students_qs:
            reasons = []
            if student.pk not in recent_active_student_ids:
                reasons.append("عدم ثبت گزارش کار در ۳ روز گذشته")

            st_reports = reports_by_student.get(student.pk, [])
            if len(st_reports) >= 2:
                latest, prev = st_reports[0], st_reports[1]
                if (
                    latest.teraze is not None
                    and prev.teraze is not None
                    and latest.teraze < prev.teraze
                ):
                    diff = round(prev.teraze - latest.teraze)
                    reasons.append(f"افت تراز ({diff} واحد) در آزمون «{latest.exam.name}»")
                elif latest.percentage < prev.percentage:
                    diff_pct = round(prev.percentage - latest.percentage, 1)
                    reasons.append(f"افت درصد ({diff_pct}٪) در آزمون «{latest.exam.name}»")
            elif len(st_reports) == 1 and st_reports[0].percentage < 40:
                reasons.append(
                    f"درصد پایین ({round(st_reports[0].percentage, 1)}٪) در آزمون «{st_reports[0].exam.name}»"
                )

            if reasons:
                risk_alerts.append(
                    {
                        "student": student,
                        "reasons": reasons,
                        "latest_report": st_reports[0] if st_reports else None,
                    }
                )

        ctx.update(
            {
                "students_count": students_count,
                "remaining_capacity": remaining_capacity,
                "pending_logs_count": pending_logs_count,
                "pending_logs": pending_logs,
                "upcoming_sessions_count": upcoming_sessions_count,
                "upcoming_sessions": upcoming_sessions,
                "average_plan_completion": average_plan_completion,
                "risk_alerts": risk_alerts[:12],
                "risk_alerts_count": len(risk_alerts),
            }
        )
        return ctx


class EditAdviserAccountView(AdviserMixin, TemplateView):
    """edit the user and adviser infos"""
    permission_field = "can_change_account"
    template_name = "adviser/account/form.html"
    redirect_url = "adviser:account"

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data.update(
            {
                "form": AdviserAccountForm(
                    initial={
                        "province": self.request.adviser.province or None,
                        "city": self.request.adviser.city or None,
                        "school": self.request.adviser.school or None,
                        "specialization": self.request.adviser.specialization or None,
                        "max_students_capacity": self.request.adviser.max_students_capacity,
                        "gender": self.request.user.gender or None,
                        "PhoneNumber": self.request.user.PhoneNumber or None,
                        "profile_image": self.request.user.profile_image or None,
                        "biography": self.request.user.biography or None,
                        "telegram_link": self.request.user.telegram_link or None,
                        "instagram_link": self.request.user.instagram_link or None,
                        "first_name": self.request.user.first_name or None,
                        "last_name": self.request.user.last_name or None,
                        "email": self.request.user.email or None,
                    }
                ),
            }
        )
        return data

    def post(self, request, *args, **kwargs):
        form = AdviserAccountForm(request.POST, request.FILES)
        if not form.is_valid():
            messages.error(request, "لطفاً اطلاعات واردشده را بررسی کنید.")
            messages.error(request, form.errors.as_ul())
            return redirect(self.redirect_url)

        data = form.cleaned_data
        user = request.user

        with transaction.atomic():
            adviser, _ = Adviser.objects.get_or_create(user=user)
            user_fields = (
                "first_name",
                "last_name",
                "email",
                "gender",
                "PhoneNumber",
                "profile_image",
                "biography",
                "telegram_link",
                "instagram_link",
            )
            changed_user_fields = []
            identity_changed = False

            for field in user_fields:
                value = data.get(field)
                if value in (None, ""):
                    continue
                if value != getattr(user, field):
                    setattr(user, field, value)
                    changed_user_fields.append(field)
                    if field in ("PhoneNumber", "email"):
                        identity_changed = True

            if identity_changed:
                user.is_verified = False
                user.is_active = False
                changed_user_fields.extend(("is_verified", "is_active"))

            new_password = data.get("password")
            if new_password:
                current_password = data.get("last_password")
                if not current_password or not user.check_password(current_password):
                    messages.error(request, "رمز فعلی صحیح نیست.")
                    return redirect(self.redirect_url)
                user.set_password(new_password)
                changed_user_fields.append("password")

            if changed_user_fields:
                user.save(update_fields=list(set(changed_user_fields)))

            adviser_fields = (
                "province",
                "city",
                "school",
                "specialization",
                "max_students_capacity",
            )
            adviser_changed = False
            for field in adviser_fields:
                value = data.get(field)
                if value not in (None, "") and value != getattr(adviser, field):
                    setattr(adviser, field, value)
                    adviser_changed = True

            if adviser_changed:
                adviser.save()

        messages.success(request, "اطلاعات حساب مشاور با موفقیت ذخیره شد.")
        if identity_changed:
            messages.warning(
                request,
                "شماره یا ایمیل تغییر کرده است؛ حساب تا تأیید مجدد غیرفعال می‌ماند.",
            )
        return redirect(self.redirect_url)
