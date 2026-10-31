from django.contrib.auth.mixins import AccessMixin
from django.contrib import messages
from django.db.models import Q
from django.shortcuts import redirect

from apps.article.models import Article
from apps.classes.models import Class
from apps.content.models import Section
from apps.exams.models import Exam
from apps.live_classes.models import (
    AdviserLiveSession,
    AdviserLiveSessionRequest,
    LiveClass,
    LiveClassRequest,
    StreamServers,
)
from apps.practice.models import Practice
from apps.schools.models import School
from apps.ticket.models import Ticket
from apps.users.advisers.models import Adviser
from apps.users.managers.models import Manager
from apps.users.students.models import Student
from apps.users.teachers.models import Teacher


class ManagerMixin(AccessMixin):
    """
    میکسین سطح دسترسی و ایزولاسیون سخت مدرسه برای پنل مدیر مدرسه (Manager Panel).
    - بررسی لاگین، فعال بودن و تایید بودن حساب کاربری
    - واکشی پروفایل Manager و School مربوط به مدیر
    - بررسی فیلد مجوز (permission_field) روی مدل Manager
    - متدهای کمکی کوئری با فیلتر سخت بر اساس School مدیر و بهینه‌سازی N+1
    """

    permission_field = None
    message_info = None
    message_success = None
    message_error = None
    message_warning = None

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, "لطفاً ابتدا وارد حساب کاربری خود شوید.")
            return redirect("user:login")

        if not request.user.is_verified or not request.user.is_active:
            messages.warning(
                request,
                "حساب کاربری شما غیرفعال یا تایید نشده است. لطفاً با پشتیبانی تماس بگیرید.",
            )
            return redirect("user:login")

        if request.user.is_superuser:
            manager, _ = Manager.objects.get_or_create(user=request.user)
            school = (
                School.objects.filter(user_manager=manager, is_active=True).first()
                or School.objects.filter(is_active=True).first()
            )
            if school is None:
                school = School.objects.create(
                    user_manager=manager,
                    name="مدرسه مرکزی",
                    province=manager.province or "تهران",
                    city=manager.city or "تهران",
                    is_active=True,
                )
        else:
            manager = (
                Manager.objects.filter(user=request.user, is_active=True)
                .select_related("user")
                .first()
            )
            if manager is None:
                messages.warning(request, "شما دارای پروفایل فعال مدیر مدرسه نیستید.")
                return redirect("user:login")

            school = (
                School.objects.filter(user_manager=manager, is_active=True)
                .select_related("user_manager__user")
                .first()
            )
            if school is None:
                messages.error(
                    request,
                    "هیچ مدرسه فعالی به حساب مدیریتی شما متصل نشده است.",
                )
                return redirect("site:main")

        if self.permission_field and self.permission_field != "ok":
            if manager is None or not getattr(manager, self.permission_field, False):
                messages.warning(
                    request,
                    "شما مجوز دسترسی به این بخش از پنل مدیریت مدرسه را ندارید.",
                )
                return redirect("manager:main")

        if request.method == "GET":
            if self.message_info:
                messages.info(request, self.message_info)
            if self.message_success:
                messages.success(request, self.message_success)
            if self.message_error:
                messages.error(request, self.message_error)
            if self.message_warning:
                messages.warning(request, self.message_warning)

        request.manager = manager
        request.school = school
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["current_manager"] = getattr(self.request, "manager", None)
        context["current_school"] = getattr(self.request, "school", None)
        return context

    def get_school(self) -> School:
        return self.request.school

    def get_school_students_queryset(self):
        school = self.get_school()
        return (
            Student.objects.filter(school=school)
            .select_related("user", "grade", "major", "adviser__user", "school")
        )

    def get_school_teachers_queryset(self):
        school = self.get_school()
        return (
            Teacher.objects.filter(school=school)
            .select_related("user", "school")
        )

    def get_school_advisers_queryset(self):
        school = self.get_school()
        return (
            Adviser.objects.filter(school=school)
            .select_related("user", "school")
        )

    def get_school_classes_queryset(self):
        school = self.get_school()
        return (
            Class.objects.filter(Q(school=school) | Q(teacher__school=school))
            .select_related("teacher__user", "grade", "major", "lesson", "school")
            .distinct()
        )

    def get_school_sections_queryset(self):
        school = self.get_school()
        return (
            Section.objects.filter(
                Q(klass__school=school) | Q(klass__teacher__school=school)
            )
            .select_related("klass", "klass__teacher__user", "klass__school")
            .distinct()
        )

    def get_school_exams_queryset(self):
        school = self.get_school()
        return (
            Exam.objects.filter(Q(school=school) | Q(teacher__school=school))
            .select_related("grade", "major", "lesson", "school")
            .prefetch_related("teacher__user")
            .distinct()
        )

    def get_school_practices_queryset(self):
        school = self.get_school()
        return (
            Practice.objects.filter(
                Q(section__klass__school=school)
                | Q(section__klass__teacher__school=school)
                | Q(creator__teacher__school=school)
            )
            .select_related(
                "section",
                "section__klass",
                "section__klass__teacher__user",
                "creator",
            )
            .distinct()
        )

    def get_school_stream_servers_queryset(self, active_only=True):
        """
        فقط سرورهای اختصاصی این مدرسه + سرورهای عمومی (school=None)
        """
        school = self.get_school()
        qs = StreamServers.objects.filter(
            Q(school=school) | Q(school__isnull=True)
        ).select_related("school")
        if active_only:
            qs = qs.filter(is_active=True)
        return qs

    def get_school_live_classes_queryset(self):
        school = self.get_school()
        return (
            LiveClass.objects.filter(
                Q(klass__school=school) | Q(klass__teacher__school=school)
            )
            .select_related(
                "klass",
                "klass__teacher__user",
                "klass__grade",
                "klass__lesson",
                "server",
                "server__school",
            )
            .distinct()
        )

    def get_school_adviser_live_sessions_queryset(self):
        school = self.get_school()
        return (
            AdviserLiveSession.objects.filter(adviser__school=school)
            .select_related(
                "adviser__user",
                "server",
                "server__school",
                "counseling_session",
            )
            .prefetch_related("students__user")
        )

    def get_school_live_requests_queryset(self):
        school = self.get_school()
        return (
            LiveClassRequest.objects.filter(teacher__school=school)
            .select_related("teacher__user")
        )

    def get_school_adviser_live_requests_queryset(self):
        school = self.get_school()
        return (
            AdviserLiveSessionRequest.objects.filter(adviser__school=school)
            .select_related("adviser__user", "counseling_session")
            .prefetch_related("students__user")
        )

    def get_school_tickets_queryset(self):
        school = self.get_school()
        return (
            Ticket.objects.filter(
                Q(school=school)
                | Q(user__student__school=school)
                | Q(user__teacher__school=school)
                | Q(user__adviser__school=school)
            )
            .select_related(
                "user",
                "school",
                "assigned_teacher__user",
                "assigned_adviser__user",
            )
            .distinct()
        )

    def get_school_articles_queryset(self):
        school = self.get_school()
        return (
            Article.objects.filter(
                Q(school=school)
                | Q(user=self.request.user)
                | Q(user__teacher__school=school)
                | Q(user__adviser__school=school)
            )
            .select_related("user", "category", "school")
            .distinct()
        )

    @staticmethod
    def toggle_object_active(obj, sync_user=False) -> bool:
        """
        قانون سخت: مدیر به هیچ وجه امکان حذف (Delete) ندارد و فقط می‌تواند
        وضعیت فعال/غیرفعال (is_active) موجودیت را تغییر دهد.
        """
        obj.is_active = not bool(obj.is_active)
        obj.save(update_fields=["is_active", "updated_at"])
        if sync_user and hasattr(obj, "user") and obj.user_id:
            obj.user.is_active = obj.is_active
            obj.user.save(update_fields=["is_active"])
        return obj.is_active
