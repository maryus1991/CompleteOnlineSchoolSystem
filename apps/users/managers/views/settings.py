from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.views.generic import ListView, TemplateView

from apps.schools.models import SchoolAnnouncement
from apps.users.managers.forms.school import (
    SchoolAnnouncementForm,
    SchoolSettingsForm,
)
from apps.users.managers.mixins import ManagerMixin


class SchoolSettingsUpdateView(ManagerMixin, TemplateView):
    template_name = "manager/settings/school_settings.html"
    permission_field = "can_manage_school_settings"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        school = self.get_school()
        if "form" not in ctx:
            ctx["form"] = SchoolSettingsForm(instance=school)
        if "announcement_form" not in ctx:
            ctx["announcement_form"] = SchoolAnnouncementForm(initial={"is_active": True})
        ctx["announcements"] = SchoolAnnouncement.objects.filter(
            school=school
        ).order_by("-is_important", "-pk")[:20]
        return ctx

    def post(self, request, *args, **kwargs):
        school = self.get_school()
        action = request.POST.get("action", "save_settings")

        if action == "create_announcement":
            a_form = SchoolAnnouncementForm(request.POST)
            if a_form.is_valid():
                ann = a_form.save(commit=False)
                ann.school = school
                ann.save()
                messages.success(request, f"اعلان «{ann.title}» با موفقیت منتشر شد.")
                return redirect("manager:school-settings")
            return self.render_to_response(
                self.get_context_data(announcement_form=a_form)
            )

        form = SchoolSettingsForm(request.POST, request.FILES, instance=school)
        if form.is_valid():
            form.save()
            messages.success(request, "تنظیمات اختصاصی مدرسه با موفقیت ذخیره شد.")
            return redirect("manager:school-settings")
        messages.error(request, "لطفاً اطلاعات واردشده را بررسی کنید.")
        return self.render_to_response(self.get_context_data(form=form))


class SchoolAnnouncementToggleActiveView(ManagerMixin, View):
    permission_field = "can_manage_school_settings"

    def post(self, request, pk, *args, **kwargs):
        ann = get_object_or_404(
            SchoolAnnouncement, pk=pk, school=self.get_school()
        )
        new_state = self.toggle_object_active(ann)
        status_label = "فعال" if new_state else "غیرفعال"
        messages.info(
            request,
            f"وضعیت اعلان «{ann.title}» به «{status_label}» تغییر یافت.",
        )
        return redirect("manager:school-settings")
