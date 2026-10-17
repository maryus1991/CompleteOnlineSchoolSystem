from django.contrib.auth.mixins import AccessMixin
from django.contrib import messages
from django.shortcuts import redirect

from apps.users.teachers.models import Teacher


class TeacherMixin(AccessMixin):
    """
    بررسی دسترسی معلم بر اساس فیلدی که در کلاس فرزند تعریف می‌شود.
    مثال:
        class ArticleCreateView(SitePermissionMixin, CreateView):
            permission_field = "can_site_article"
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
                "حساب شما فعال نشده یا تایید نشده است لطفا با ادمین در ارتباط باشید"
            )
            return redirect("user:login")


        if  request.user.is_superuser:
            teacher = Teacher.objects.get_or_create(user=request.user)[0]

        else:
            teacher = Teacher.objects.filter(
                user=request.user
            ).first()

        if teacher is None and not request.user.is_superuser:
            messages.warning(
                request,
                " شما دارای پروفایل معلمی نیستید"

            )
            return redirect("user:login")

        if self.permission_field != "ok" and self.permission_field:
            if teacher is None or not getattr(teacher, self.permission_field, False):
                messages.warning(request, "شما اجازه ورود به این صفحه ندارید")
                return redirect("teacher:main")

        if request.method == "GET":
            if self.message_info :
                messages.info(request, self.message_info)
            if self.message_success :
                messages.success(request, self.message_success)
            if self.message_error :
                messages.error(request, self.message_error)
            if self.message_warning :
                messages.warning(request, self.message_warning)

        request.teacher = teacher

        return super().dispatch(request, *args, **kwargs)



