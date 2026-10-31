from django.contrib import messages
from django.db import transaction
from django.db.models import Avg, Count, Q
from django.shortcuts import redirect
from django.views.generic import TemplateView

from apps.exams.models import Exam
from apps.live_classes.models import AdviserLiveSession, LiveClass
from apps.schools.models import SchoolAnnouncement
from apps.ticket.models import Ticket
from apps.users.managers.forms.users import ManagerAccountForm
from apps.users.managers.mixins import ManagerMixin


class ManagerDashboardView(ManagerMixin, TemplateView):
    template_name = "manager/dashboard.html"
    permission_field = "ok"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        school = self.get_school()

        students_qs = self.get_school_students_queryset()
        teachers_qs = self.get_school_teachers_queryset()
        advisers_qs = self.get_school_advisers_queryset()
        classes_qs = self.get_school_classes_queryset()
        exams_qs = self.get_school_exams_queryset()
        live_classes_qs = self.get_school_live_classes_queryset()
        adviser_live_qs = self.get_school_adviser_live_sessions_queryset()
        tickets_qs = self.get_school_tickets_queryset()

        # کارت‌های آماری زنده (Live KPI Cards)
        ctx["active_students_count"] = students_qs.filter(is_active=True).count()
        ctx["total_students_count"] = students_qs.count()
        ctx["active_teachers_count"] = teachers_qs.filter(is_active=True).count()
        ctx["active_advisers_count"] = advisers_qs.filter(is_active=True).count()
        ctx["active_classes_count"] = classes_qs.filter(is_active=True).count()
        ctx["running_exams_count"] = exams_qs.filter(
            is_active=True,
            status__in=[Exam.ExamStatus.STARTED, Exam.ExamStatus.WAITING_START],
        ).count()
        ctx["live_online_classes_count"] = (
            live_classes_qs.filter(is_active=True, status=LiveClass.Status.LIVE).count()
            + adviser_live_qs.filter(
                is_active=True, status=AdviserLiveSession.Status.LIVE
            ).count()
        )
        ctx["open_tickets_count"] = tickets_qs.filter(
            is_active=True, status=Ticket.TicketStatus.awating_admin
        ).count()

        # نمودار ۱: توزیع دانش‌آموزان فعال بر اساس پایه تحصیلی
        students_by_grade = list(
            students_qs.filter(is_active=True)
            .values("grade__name")
            .annotate(total=Count("id"))
            .order_by("-total")
        )
        max_grade_count = max((item["total"] for item in students_by_grade), default=1)
        for item in students_by_grade:
            item["label"] = item["grade__name"] or "تعیین‌نشده"
            item["percent"] = round((item["total"] / max_grade_count) * 100)
        ctx["students_by_grade"] = students_by_grade

        # نمودار ۲: وضعیت آزمون‌های مدرسه
        exams_by_status = list(
            exams_qs.filter(is_active=True)
            .values("status")
            .annotate(total=Count("id"))
            .order_by("-total")
        )
        max_exam_count = max((item["total"] for item in exams_by_status), default=1)
        for item in exams_by_status:
            item["label"] = item["status"] or "نامشخص"
            item["percent"] = round((item["total"] / max_exam_count) * 100)
        ctx["exams_by_status"] = exams_by_status

        # آخرین تیکت‌های باز مدرسه
        ctx["open_tickets"] = tickets_qs.filter(
            is_active=True,
            status__in=[
                Ticket.TicketStatus.awating_admin,
                Ticket.TicketStatus.awating_user,
            ],
        ).order_by("-id")[:6]

        # آخرین فعالیت‌ها (کلاس‌ها، آزمون‌ها و دانش‌آموزان جدید)
        ctx["recent_classes"] = classes_qs.order_by("-pk")[:5]
        ctx["recent_exams"] = exams_qs.order_by("-pk")[:5]
        ctx["recent_students"] = students_qs.order_by("-pk")[:5]

        # اعلان‌های مهم مدرسه
        ctx["important_announcements"] = SchoolAnnouncement.objects.filter(
            school=school, is_active=True
        ).order_by("-is_important", "-pk")[:5]

        return ctx


class ManagerEditAccountView(ManagerMixin, TemplateView):
    template_name = "manager/account_form.html"
    permission_field = "can_change_account"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        manager = self.request.manager
        ctx["form"] = ManagerAccountForm(
            initial={
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "gender": user.gender,
                "province": manager.province,
                "city": manager.city,
                "biography": user.biography,
                "telegram_link": user.telegram_link,
                "instagram_link": user.instagram_link,
            }
        )
        return ctx

    def post(self, request, *args, **kwargs):
        form = ManagerAccountForm(request.POST, request.FILES)
        if not form.is_valid():
            messages.error(request, "لطفاً اطلاعات واردشده را بررسی کنید.")
            return self.render_to_response(self.get_context_data(form=form))

        data = form.cleaned_data
        user = request.user
        manager = request.manager
        with transaction.atomic():
            user.first_name = data["first_name"]
            user.last_name = data["last_name"]
            user.email = data.get("email") or ""
            user.gender = data["gender"]
            user.biography = data.get("biography") or ""
            user.telegram_link = data.get("telegram_link") or None
            user.instagram_link = data.get("instagram_link") or None
            if data.get("profile_image"):
                user.profile_image = data["profile_image"]
            user.save()

            manager.province = data.get("province") or ""
            manager.city = data.get("city") or ""
            manager.save(update_fields=["province", "city", "updated_at"])

        messages.success(request, "اطلاعات حساب مدیر مدرسه با موفقیت بروزرسانی شد.")
        return redirect("manager:account")
