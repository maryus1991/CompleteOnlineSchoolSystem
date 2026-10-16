from django.contrib.auth.mixins import AccessMixin
from django.contrib import messages
from django.shortcuts import redirect

from apps.users.teachers.models import Teacher


class TeacherMixin(AccessMixin):

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

        request.teacher = teacher

        return super().dispatch(request, *args, **kwargs)



