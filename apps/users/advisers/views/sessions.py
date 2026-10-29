from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import CreateView, ListView, UpdateView
from apps.progress.models import CounselingSession
from apps.sitesetting.models import Counseling
from apps.users.advisers.forms.session import (
    CounselingSessionForm,
    SiteCounselingFollowUpForm,
)
from apps.users.advisers.mixins import AdviserMixin


class CounselingSessionListView(AdviserMixin, ListView):
    """Counseling sections list"""
    permission_field = "can_manage_sessions"
    template_name = "adviser/sessions/list.html"
    context_object_name = "items"
    paginate_by = 50

    def get_queryset(self):
        qs = (
            CounselingSession.objects.filter(
                adviser=self.request.adviser,
                student__in=self.get_adviser_students_queryset(),
                is_active=True,
            )
            .select_related("student", "student__user", "adviser", "adviser__user")
            .order_by("-scheduled_at", "-pk")
        )
        status = self.request.GET.get("status")
        student_id = self.request.GET.get("student")
        if status:
            qs = qs.filter(status=status)
        if student_id and student_id.isdigit():
            qs = qs.filter(student_id=int(student_id))
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["students"] = self.get_adviser_students_queryset()
        ctx["statuses"] = CounselingSession.Status.choices
        ctx["selected_status"] = self.request.GET.get("status", "")
        ctx["selected_student"] = self.request.GET.get("student", "")
        return ctx


class CounselingSessionCreateView(AdviserMixin, CreateView):
    """create section for adviser"""
    permission_field = "can_manage_sessions"
    model = CounselingSession
    form_class = CounselingSessionForm
    template_name = "adviser/sessions/form.html"
    success_url = reverse_lazy("adviser:session-list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["adviser"] = self.request.adviser
        return kwargs

    def get_initial(self):
        initial = super().get_initial()
        initial["status"] = CounselingSession.Status.SCHEDULED
        student_id = self.request.GET.get("student")
        if student_id and student_id.isdigit():
            initial["student"] = int(student_id)
        return initial

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["page_title"] = "تنظیم جلسه مشاوره جدید"
        ctx["page_subtitle"] = "زمان‌بندی جلسه آنلاین، تلفنی یا حضوری با دانش‌آموز"
        ctx["is_update"] = False
        return ctx

    def form_valid(self, form):
        student = form.cleaned_data["student"]
        if not self.get_adviser_students_queryset().filter(pk=student.pk).exists():
            messages.error(self.request, "این دانش‌آموز تحت پوشش شما نیست.")
            return self.form_invalid(form)
        form.instance.adviser = self.request.adviser
        messages.success(self.request, "جلسه مشاوره با موفقیت تنظیم شد.")
        return super().form_valid(form)


class CounselingSessionUpdateView(AdviserMixin, UpdateView):
    """update the section list """
    permission_field = "can_manage_sessions"
    model = CounselingSession
    form_class = CounselingSessionForm
    template_name = "adviser/sessions/form.html"
    context_object_name = "session"
    success_url = reverse_lazy("adviser:session-list")

    def get_queryset(self):
        return CounselingSession.objects.filter(
            adviser=self.request.adviser,
            student__in=self.get_adviser_students_queryset(),
            is_active=True,
        ).select_related("student", "student__user")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["adviser"] = self.request.adviser
        return kwargs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["page_title"] = "مدیریت و ثبت صورت‌جلسه مشاوره"
        ctx["page_subtitle"] = f"{self.object.title} — {self.object.student}"
        ctx["is_update"] = True
        return ctx

    def form_valid(self, form):
        student = form.cleaned_data["student"]
        if not self.get_adviser_students_queryset().filter(pk=student.pk).exists():
            messages.error(self.request, "این دانش‌آموز تحت پوشش شما نیست.")
            return self.form_invalid(form)
        messages.success(self.request, "اطلاعات جلسه و صورت‌جلسه با موفقیت بروزرسانی شد.")
        return super().form_valid(form)


class SiteCounselingRequestListView(AdviserMixin, ListView):
    """manage the counseling request that submitted in main page"""
    permission_field = "can_answer_counseling_requests"
    template_name = "adviser/sessions/site_requests.html"
    context_object_name = "items"
    paginate_by = 50

    def get_queryset(self):
        qs = (
            Counseling.objects.filter(is_active=True)
            .select_related("assigned_adviser", "assigned_adviser__user")
            .order_by("read", "-pk")
        )
        status = self.request.GET.get("status")
        if status:
            qs = qs.filter(status=status)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["statuses"] = Counseling.Status.choices
        ctx["selected_status"] = self.request.GET.get("status", "")
        return ctx


class SiteCounselingRequestUpdateView(AdviserMixin, View):
    """set the result of counseling request"""
    permission_field = "can_answer_counseling_requests"

    def post(self, request, *args, **kwargs):
        req_obj = get_object_or_404(
            Counseling.objects.filter(is_active=True),
            pk=kwargs["pk"],
        )
        form = SiteCounselingFollowUpForm(request.POST, instance=req_obj)
        if form.is_valid():
            updated = form.save(commit=False)
            updated.assigned_adviser = request.adviser
            updated.read = True
            updated.save(update_fields=["status", "read", "adviser_follow_up_note", "assigned_adviser"])
            messages.success(request, "وضعیت درخواست مشاوره سایت بروزرسانی شد.")
        else:
            messages.error(request, "خطا در بروزرسانی درخواست مشاوره.")
        return redirect("adviser:site-requests")
