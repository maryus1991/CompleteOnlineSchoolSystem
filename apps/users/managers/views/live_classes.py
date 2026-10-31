from django.contrib import messages
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.views.generic import ListView, TemplateView

from apps.live_classes.models import (
    AdviserLiveSession,
    LiveClass,
)
from apps.users.managers.forms.live_classes import (
    ManagerAdviserLiveSessionForm,
    ManagerLiveClassForm,
    ManagerLiveRequestReviewForm,
)
from apps.users.managers.mixins import ManagerMixin


class LiveClassListView(ManagerMixin, ListView):
    template_name = "manager/live_classes/live_list.html"
    context_object_name = "live_classes"
    paginate_by = 20
    permission_field = "can_manage_live_classes"

    def get_queryset(self):
        qs = self.get_school_live_classes_queryset().order_by("-pk")
        status = (self.request.GET.get("status") or "").strip()
        server_id = (self.request.GET.get("server") or "").strip()
        if status:
            qs = qs.filter(status=status)
        if server_id.isdigit():
            qs = qs.filter(server_id=int(server_id))
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["adviser_live_sessions"] = (
            self.get_school_adviser_live_sessions_queryset().order_by("-pk")[:20]
        )
        ctx["teacher_live_requests"] = (
            self.get_school_live_requests_queryset().order_by("-pk")[:15]
        )
        ctx["adviser_live_requests"] = (
            self.get_school_adviser_live_requests_queryset().order_by("-pk")[:15]
        )
        ctx["available_servers"] = self.get_school_stream_servers_queryset(
            active_only=False
        )
        ctx["live_statuses"] = LiveClass.Status.choices
        return ctx


class LiveClassCreateView(ManagerMixin, TemplateView):
    template_name = "manager/live_classes/live_form.html"
    permission_field = "can_manage_live_classes"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["is_edit"] = False
        if "form" not in ctx:
            ctx["form"] = ManagerLiveClassForm(school=self.get_school())
        return ctx

    def post(self, request, *args, **kwargs):
        school = self.get_school()
        form = ManagerLiveClassForm(request.POST, school=school)
        if form.is_valid():
            live_obj = form.save()
            messages.success(
                request,
                f"کلاس آنلاین «{live_obj.klass.name}» روی سرور «{live_obj.server.name}» ایجاد شد.",
            )
            return redirect("manager:live-list")
        messages.error(request, "لطفاً اطلاعات فرم کلاس آنلاین را بررسی کنید.")
        return self.render_to_response(self.get_context_data(form=form))


class LiveClassUpdateView(ManagerMixin, TemplateView):
    template_name = "manager/live_classes/live_form.html"
    permission_field = "can_manage_live_classes"

    def get_live_obj(self):
        return get_object_or_404(
            self.get_school_live_classes_queryset(), pk=self.kwargs["pk"]
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        live_obj = self.get_live_obj()
        ctx["live_obj"] = live_obj
        ctx["is_edit"] = True
        if "form" not in ctx:
            ctx["form"] = ManagerLiveClassForm(
                instance=live_obj, school=self.get_school()
            )
        return ctx

    def post(self, request, *args, **kwargs):
        live_obj = self.get_live_obj()
        form = ManagerLiveClassForm(
            request.POST, instance=live_obj, school=self.get_school()
        )
        if form.is_valid():
            form.save()
            messages.success(request, "کلاس آنلاین با موفقیت ویرایش شد.")
            return redirect("manager:live-list")
        return self.render_to_response(self.get_context_data(form=form))


class LiveClassToggleActiveView(ManagerMixin, View):
    permission_field = "can_manage_live_classes"

    def post(self, request, pk, *args, **kwargs):
        live_obj = get_object_or_404(self.get_school_live_classes_queryset(), pk=pk)
        new_state = self.toggle_object_active(live_obj)
        status_label = "فعال" if new_state else "غیرفعال"
        messages.info(
            request,
            f"وضعیت کلاس آنلاین «{live_obj.klass.name}» به «{status_label}» تغییر یافت.",
        )
        return redirect(request.META.get("HTTP_REFERER") or "manager:live-list")


class AdviserLiveSessionCreateView(ManagerMixin, TemplateView):
    template_name = "manager/live_classes/adviser_live_form.html"
    permission_field = "can_manage_live_classes"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        if "form" not in ctx:
            ctx["form"] = ManagerAdviserLiveSessionForm(school=self.get_school())
        return ctx

    def post(self, request, *args, **kwargs):
        form = ManagerAdviserLiveSessionForm(request.POST, school=self.get_school())
        if form.is_valid():
            obj = form.save()
            messages.success(
                request,
                f"جلسه آنلاین مشاوره «{obj.title}» با موفقیت ایجاد شد.",
            )
            return redirect("manager:live-list")
        return self.render_to_response(self.get_context_data(form=form))


class StreamServerMonitorView(ManagerMixin, TemplateView):
    """
    مانیتورینگ سرورهای استریم مدرسه (سرورهای اختصاصی مدرسه + سرورهای عمومی).
    """

    template_name = "manager/live_classes/server_monitor.html"
    permission_field = "can_manage_live_classes"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        school = self.get_school()
        servers_qs = (
            self.get_school_stream_servers_queryset(active_only=False)
            .annotate(
                school_running_classes=Count(
                    "live",
                    filter=Q(
                        live__status=LiveClass.Status.LIVE,
                        live__is_active=True,
                        live__klass__school=school,
                    ),
                    distinct=True,
                ),
                total_running_classes=Count(
                    "live",
                    filter=Q(live__status=LiveClass.Status.LIVE, live__is_active=True),
                    distinct=True,
                ),
                school_running_adviser_sessions=Count(
                    "adviser_live_sessions",
                    filter=Q(
                        adviser_live_sessions__status=AdviserLiveSession.Status.LIVE,
                        adviser_live_sessions__is_active=True,
                        adviser_live_sessions__adviser__school=school,
                    ),
                    distinct=True,
                ),
                school_total_classes=Count(
                    "live",
                    filter=Q(live__klass__school=school),
                    distinct=True,
                ),
            )
            .order_by("-is_active", "-pk")
        )
        ctx["servers"] = servers_qs
        return ctx


class LiveRequestReviewView(ManagerMixin, View):
    permission_field = "can_manage_live_classes"

    def post(self, request, kind, pk, *args, **kwargs):
        form = ManagerLiveRequestReviewForm(request.POST)
        if not form.is_valid():
            messages.error(request, "وضعیت ارسالی معتبر نیست.")
            return redirect("manager:live-list")

        if kind == "teacher":
            req_obj = get_object_or_404(self.get_school_live_requests_queryset(), pk=pk)
        else:
            req_obj = get_object_or_404(
                self.get_school_adviser_live_requests_queryset(), pk=pk
            )

        req_obj.status = form.cleaned_data["status"]
        req_obj.admin_note = form.cleaned_data.get("admin_note") or ""
        req_obj.save(update_fields=["status", "admin_note", "updated_at"])
        messages.success(request, f"وضعیت درخواست «{req_obj.title}» بروزرسانی شد.")
        return redirect("manager:live-list")
