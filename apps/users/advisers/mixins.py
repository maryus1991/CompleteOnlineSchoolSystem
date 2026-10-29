from django.contrib.auth.mixins import AccessMixin
from django.contrib import messages
from django.shortcuts import redirect
from apps.users.advisers.models import Adviser
from apps.users.students.models import Student


class AdviserMixin(AccessMixin):
    """
    بررسی دسترسی مشاور بر اساس فیلدی که در کلاس فرزند تعریف می‌شود.
    مثال:
        class StudyPlanCreateView(AdviserMixin, CreateView):
            permission_field = "can_manage_study_plans"
    """
    permission_field = None
    message_info = None
    message_success = None
    message_error = None
    message_warning = None

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, "لطفا وارد سایت شوید")
            return redirect("user:login")

        if not request.user.is_verified or not request.user.is_active:
            messages.warning(
                request,
                "حساب شما فعال نشده یا تایید نشده است لطفا با ادمین در ارتباط باشید",
            )
            return redirect("user:login")

        if request.user.is_superuser:
            adviser = Adviser.objects.get_or_create(user=request.user)[0]
        else:
            adviser = (
                Adviser.objects.filter(user=request.user)
                .select_related("user", "school")
                .first()
            )

        if adviser is None and not request.user.is_superuser:
            messages.warning(request, "شما دارای پروفایل مشاور نیستید")
            return redirect("user:login")

        if self.permission_field and self.permission_field != "ok":
            if adviser is None or not getattr(adviser, self.permission_field, False):
                messages.warning(request, "شما اجازه ورود به این صفحه ندارید")
                return redirect("adviser:main")

        if request.method == "GET":
            if self.message_info:
                messages.info(request, self.message_info)
            if self.message_success:
                messages.success(request, self.message_success)
            if self.message_error:
                messages.error(request, self.message_error)
            if self.message_warning:
                messages.warning(request, self.message_warning)

        request.adviser = adviser
        return super().dispatch(request, *args, **kwargs)

    def get_adviser_students_queryset(self):
        """فقط دانش‌آموزان تحت پوشش همین مشاور را برمی‌گرداند (Data Isolation)"""
        if self.request.user.is_superuser and not self.request.adviser.students.exists():
            return Student.objects.filter(is_active=True).select_related(
                "user", "grade", "major", "school", "adviser"
            )
        return (
            self.request.adviser.students.filter(is_active=True).select_related(
                "user", "grade", "major", "school", "adviser"
            )
        )
