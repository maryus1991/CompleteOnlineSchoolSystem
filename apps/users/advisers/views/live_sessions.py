from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from apps.live_classes.models import (
    AdviserLiveSession,
    AdviserLiveSessionReport,
    AdviserLiveSessionRequest,
)
from apps.users.advisers.forms.live_session import (
    AdviserLiveSessionForm,
    AdviserLiveSessionReportForm,
    AdviserLiveSessionRequestForm,
)
from apps.users.advisers.mixins import AdviserMixin


# ══════════════════════════════════════════════════════════
# درخواست تشکیل جلسه آنلاین مشاوره
# ══════════════════════════════════════════════════════════


class AdviserLiveRequestListView(AdviserMixin, ListView):
    permission_field = "can_start_live_session"
    template_name = "adviser/live/live_request_list.html"
    context_object_name = "items"
    paginate_by = 20

    def get_queryset(self):
        return (
            AdviserLiveSessionRequest.objects.filter(
                adviser=self.request.adviser,
                is_active=True,
            )
            .select_related("counseling_session", "counseling_session__student", "counseling_session__student__user")
            .prefetch_related("students", "students__user")
            .order_by("-pk")
        )


class AdviserLiveRequestCreateView(AdviserMixin, CreateView):
    permission_field = "can_start_live_session"
    model = AdviserLiveSessionRequest
    form_class = AdviserLiveSessionRequestForm
    template_name = "adviser/live/live_request_form.html"
    success_url = reverse_lazy("adviser:live-request-list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["adviser"] = self.request.adviser
        return kwargs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["page_title"] = "درخواست تشکیل جلسه آنلاین مشاوره"
        ctx["is_update"] = False
        return ctx

    def form_valid(self, form):
        form.instance.adviser = self.request.adviser
        form.instance.status = AdviserLiveSessionRequest.Status.PENDING
        response = super().form_valid(form)
        if self.object.counseling_session and self.object.counseling_session.student_id:
            self.object.students.add(self.object.counseling_session.student)
        messages.success(self.request, "درخواست جلسه آنلاین مشاوره ثبت شد و در انتظار بررسی است.")
        return response


class AdviserLiveRequestUpdateView(AdviserMixin, UpdateView):
    permission_field = "can_start_live_session"
    model = AdviserLiveSessionRequest
    form_class = AdviserLiveSessionRequestForm
    template_name = "adviser/live/live_request_form.html"
    context_object_name = "live_request"
    success_url = reverse_lazy("adviser:live-request-list")

    def get_queryset(self):
        return AdviserLiveSessionRequest.objects.filter(
            adviser=self.request.adviser,
            is_active=True,
            status=AdviserLiveSessionRequest.Status.PENDING,
        )

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["adviser"] = self.request.adviser
        return kwargs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["page_title"] = "ویرایش درخواست جلسه آنلاین مشاوره"
        ctx["is_update"] = True
        return ctx

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.object.counseling_session and self.object.counseling_session.student_id:
            self.object.students.add(self.object.counseling_session.student)
        messages.success(self.request, "درخواست جلسه آنلاین بروزرسانی شد.")
        return response


class AdviserLiveRequestDeleteView(AdviserMixin, DeleteView):
    permission_field = "can_start_live_session"
    model = AdviserLiveSessionRequest
    template_name = "adviser/live/confirm_delete.html"
    success_url = reverse_lazy("adviser:live-request-list")
    context_object_name = "object"

    def get_queryset(self):
        return AdviserLiveSessionRequest.objects.filter(
            adviser=self.request.adviser,
            is_active=True,
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["object_label"] = f"درخواست «{self.object.title}»"
        ctx["back_url"] = reverse("adviser:live-request-list")
        return ctx

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.is_active = False
        self.object.save(update_fields=["is_active"])
        messages.success(request, "درخواست جلسه آنلاین حذف شد.")
        return HttpResponseRedirect(self.get_success_url())

    def form_valid(self, form):
        return self.delete(self.request)


class AdviserLiveRequestDetailView(AdviserMixin, DetailView):
    permission_field = "can_start_live_session"
    model = AdviserLiveSessionRequest
    template_name = "adviser/live/live_request_detail.html"
    context_object_name = "live_request"

    def get_queryset(self):
        return (
            AdviserLiveSessionRequest.objects.filter(
                adviser=self.request.adviser,
                is_active=True,
            )
            .select_related("counseling_session", "counseling_session__student", "counseling_session__student__user")
            .prefetch_related("students", "students__user")
        )


# ══════════════════════════════════════════════════════════
# مدیریت و ورود مشاور به جلسات آنلاین مشاوره
# ══════════════════════════════════════════════════════════


class AdviserLiveSessionListView(AdviserMixin, ListView):
    permission_field = "can_start_live_session"
    template_name = "adviser/live/live_list.html"
    context_object_name = "items"
    paginate_by = 20

    def get_queryset(self):
        qs = (
            AdviserLiveSession.objects.filter(
                is_active=True,
                adviser=self.request.adviser,
            )
            .select_related(
                "server",
                "counseling_session",
                "counseling_session__student",
                "counseling_session__student__user",
            )
            .prefetch_related("students", "students__user", "report")
            .order_by("-pk")
        )
        for item in qs:
            item.report_obj = next(
                (r for r in item.report.all() if r.is_active),
                None,
            )
        return qs


class AdviserLiveSessionUpdateView(AdviserMixin, UpdateView):
    """ویرایش جلسه آنلاین مشاوره"""
    permission_field = "can_start_live_session"
    model = AdviserLiveSession
    form_class = AdviserLiveSessionForm
    template_name = "adviser/live/live_form.html"
    context_object_name = "live"

    def get_queryset(self):
        return (
            AdviserLiveSession.objects.filter(
                is_active=True,
                adviser=self.request.adviser,
            )
            .select_related("server", "counseling_session")
            .prefetch_related("students")
        )

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["adviser"] = self.request.adviser
        return kwargs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["page_title"] = "ویرایش جلسه آنلاین مشاوره"
        ctx["is_update"] = True
        return ctx

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.object.counseling_session and self.object.counseling_session.student_id:
            self.object.students.add(self.object.counseling_session.student)
        messages.success(self.request, "جلسه آنلاین مشاوره بروزرسانی شد.")
        return response

    def get_success_url(self):
        return reverse("adviser:live-session-list")


class AdviserLiveSessionSetStatusView(AdviserMixin, View):
    """تغییر وضعیت سریع جلسه آنلاین مشاوره"""
    permission_field = "can_start_live_session"
    ALLOWED = {
        AdviserLiveSession.Status.LIVE,
        AdviserLiveSession.Status.COMPLETED,
        AdviserLiveSession.Status.CANCELLED,
        AdviserLiveSession.Status.SCHEDULED,
    }

    def post(self, request, pk):
        live = get_object_or_404(
            AdviserLiveSession,
            pk=pk,
            is_active=True,
            adviser=request.adviser,
        )
        status = request.POST.get("status")
        if status not in self.ALLOWED:
            messages.error(request, "وضعیت نامعتبر است.")
            return redirect("adviser:live-session-list")

        live.status = status
        live.save(update_fields=["status"])
        messages.success(request, f"وضعیت جلسه آنلاین تغییر یافت: {live.get_status_display()}")
        return redirect("adviser:live-session-list")


class AdviserLiveJoinView(AdviserMixin, View):
    """ورود مشاور به اتاق جلسه آنلاین (و فعال‌سازی خودکار وضعیت LIVE)"""
    permission_field = "can_start_live_session"

    def get(self, request, pk):
        live = get_object_or_404(
            AdviserLiveSession.objects.select_related(
                "server",
                "adviser",
                "adviser__user",
                "counseling_session",
            ),
            pk=pk,
            is_active=True,
            adviser=request.adviser,
        )

        # ورود مشاور = خودکار وضعیت جلسه را LIVE کن
        if live.status != AdviserLiveSession.Status.LIVE:
            live.status = AdviserLiveSession.Status.LIVE
            live.save(update_fields=["status"])

        url = live.adviser_meeting_url
        if not url:
            messages.warning(request, "لینک ورود به جلسه آنلاین ساخته نشد. سرور را بررسی کنید.")
            return redirect("adviser:live-session-list")

        return redirect(url)


# ══════════════════════════════════════════════════════════
# ثبت و ویرایش گزارش جلسه آنلاین مشاوره
# ══════════════════════════════════════════════════════════


class AdviserLiveReportCreateView(AdviserMixin, CreateView):
    """ثبت گزارش برای یک جلسه آنلاین مشاوره"""
    permission_field = "can_start_live_session"
    model = AdviserLiveSessionReport
    form_class = AdviserLiveSessionReportForm
    template_name = "adviser/live/live_report_form.html"

    def get_live(self):
        return get_object_or_404(
            AdviserLiveSession.objects.select_related("server", "counseling_session"),
            pk=self.kwargs["live_pk"],
            is_active=True,
            adviser=self.request.adviser,
        )

    def get_existing_report(self, live=None):
        live = live or self.get_live()
        return AdviserLiveSessionReport.objects.filter(
            live_session=live,
            is_active=True,
        ).first()

    def get(self, request, *args, **kwargs):
        self.live = self.get_live()
        existing = self.get_existing_report(live=self.live)
        if existing:
            return redirect("adviser:live-report-update", pk=existing.pk)
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.live = self.get_live()
        existing = self.get_existing_report(live=self.live)
        if existing:
            return redirect("adviser:live-report-update", pk=existing.pk)
        return super().post(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["adviser"] = self.request.adviser
        return kwargs

    def get_initial(self):
        initial = super().get_initial()
        live = getattr(self, "live", None) or self.get_live()
        if live.counseling_session_id:
            initial["counseling_session"] = live.counseling_session_id
        return initial

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        live = getattr(self, "live", None) or self.get_live()
        ctx["live"] = live
        ctx["page_title"] = "ثبت گزارش جلسه آنلاین مشاوره"
        ctx["is_update"] = False
        return ctx

    def form_valid(self, form):
        live = self.get_live()
        existing = self.get_existing_report(live=live)
        if existing:
            return redirect("adviser:live-report-update", pk=existing.pk)

        form.instance.live_session = live
        if not form.instance.counseling_session_id and live.counseling_session_id:
            form.instance.counseling_session_id = live.counseling_session_id
        messages.success(self.request, "گزارش جلسه آنلاین مشاوره با موفقیت ثبت شد.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("adviser:live-session-list")


class AdviserLiveReportUpdateView(AdviserMixin, UpdateView):
    """ویرایش گزارش جلسه آنلاین مشاوره"""
    permission_field = "can_start_live_session"
    model = AdviserLiveSessionReport
    form_class = AdviserLiveSessionReportForm
    template_name = "adviser/live/live_report_form.html"
    context_object_name = "report"

    def get_queryset(self):
        return (
            AdviserLiveSessionReport.objects.filter(
                is_active=True,
                live_session__is_active=True,
                live_session__adviser=self.request.adviser,
            )
            .select_related(
                "live_session",
                "live_session__server",
                "counseling_session",
            )
        )

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["adviser"] = self.request.adviser
        return kwargs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["live"] = self.object.live_session
        ctx["page_title"] = "ویرایش گزارش جلسه آنلاین مشاوره"
        ctx["is_update"] = True
        return ctx

    def form_valid(self, form):
        messages.success(self.request, "گزارش جلسه آنلاین مشاوره بروزرسانی شد.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("adviser:live-session-list")
