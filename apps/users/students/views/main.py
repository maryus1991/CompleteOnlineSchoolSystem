

from django.views.generic import TemplateView
from apps.users.students.mixins import StudentMixin
from apps.users.students.forms.auth import StudentForm
from django.contrib import messages

from django.db import transaction
from django.shortcuts import redirect

from apps.users.students.models import Student


class MainStudentDashboardView(StudentMixin, TemplateView):
    """student dashboard view"""

    template_name = 'dashboard/main.html'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)

        return data

class EditAccountView(StudentMixin, TemplateView):
    """edit account dashboard view"""

    template_name = 'dashboard/account/account.html'
    redirect_url = "student:account"


    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data.update({
            "form": StudentForm(initial={
                "grade": self.request.student.grade or None ,
                "major": self.request.student.major or None ,
                "province": self.request.student.province or None ,
                "city": self.request.student.city or None ,
                "school": self.request.student.school or None ,
                "gender": self.request.user.gender or None,
                "PhoneNumber": self.request.user.PhoneNumber or None,
                "profile_image": self.request.user.profile_image or None,
                "biography": self.request.user.biography or None,
                "parent_phone_number":  self.request.student.parent_phone_number or None,
                "telegram_link": self.request.user.telegram_link or None,
                "instagram_link": self.request.user.instagram_link or None,
                "first_name": self.request.user.first_name or None,
                "last_name": self.request.user.last_name or None,
                "email": self.request.user.email or None,
            }),
        })
        return data


    def post(self, request, *args, **kwargs):
        form = StudentForm(request.POST, request.FILES)

        if not form.is_valid():
            messages.error(request, "لطفاً اطلاعات واردشده را بررسی کنید.")
            return redirect(self.redirect_url)

        data = form.cleaned_data
        user = request.user

        with transaction.atomic():
            student, _ = Student.objects.get_or_create(user=user)

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

            student_fields = (
                "grade",
                "major",
                "province",
                "city",
                "parent_phone_number",
                "school",
            )

            student_changed = False

            for field in student_fields:
                value = data.get(field)

                if value not in (None, "") and value != getattr(student, field):
                    setattr(student, field, value)
                    student_changed = True

            if student_changed:
                student.save()

        messages.success(request, "اطلاعات با موفقیت ذخیره شد.")

        if identity_changed:
            messages.warning(
                request,
                "شماره یا ایمیل تغییر کرده است؛ حساب تا تأیید مجدد غیرفعال می‌ماند.",
            )

        return redirect(self.redirect_url)

