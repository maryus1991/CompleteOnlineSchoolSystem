

from django.contrib import messages
from django.db.models import Count, Prefetch, Q
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from apps.classes.models import Class
from apps.content.models import ClassArticle, ClassFile, Section
from apps.live_classes.models import LiveClass, LiveClassRequest, LiveClassReport
from apps.practice.models import Practice
from apps.users.teachers.forms.classes import (
    ClassArticleForm,
    ClassFileForm,
    LiveClassRequestForm,
    SectionForm,
    LiveClassForm,
    LiveClassReportForm,
)
from apps.users.teachers.mixins import TeacherMixin


def _teacher_classes(teacher):
    return Class.objects.filter(teacher=teacher, is_active=True).select_related(
        "major", "lesson", "grade"
    )


def _teacher_sections(teacher):
    return Section.objects.filter(
        is_active=True,
        klass__teacher=teacher,
        klass__is_active=True,
    )


def _get_teacher_class(teacher, pk):
    return get_object_or_404(_teacher_classes(teacher), pk=pk)


class SectionDeleteView(TeacherMixin, DeleteView):
    permission_field = "can_add_class_section"
    model = Section
    template_name = "teacher/class/confirm_delete.html"
    context_object_name = "object"

    def get_queryset(self):
        return _teacher_sections(self.request.teacher)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["object_label"] = f"جلسه «{self.object.name}»"
        ctx["back_url"] = reverse(
            "teacher:class-sections", kwargs={"pk": self.object.klass_id}
        )
        return ctx

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        klass_id = self.object.klass_id
        self.object.is_active = False
        self.object.save(update_fields=["is_active"])
        messages.success(request, "جلسه حذف شد.")
        return HttpResponseRedirect(
            reverse("teacher:class-sections", kwargs={"pk": klass_id})
        )

    def form_valid(self, form):
        return self.delete(self.request)


# ══════════════════════════════════════════════════════════
# جزئیات جلسه (مقاله / فایل / تمرین) + دکمه ورود به کلاس آنلاین
# ══════════════════════════════════════════════════════════

class SectionDetailView(TeacherMixin, DetailView):
    permission_field = "ok"
    model = Section
    template_name = "teacher/class/section_detail.html"
    context_object_name = "section"

    def get_queryset(self):
        return (
            _teacher_sections(self.request.teacher)
            .select_related(
                "klass",
                "klass__grade",
                "klass__major",
                "klass__lesson",
                "klass__teacher__user",
            )
            .prefetch_related(
                Prefetch(
                    "article",
                    queryset=ClassArticle.objects.filter(is_active=True).order_by(
                        "-sort_number", "pk"
                    ),
                    to_attr="articles_list",
                ),
                Prefetch(
                    "file",
                    queryset=ClassFile.objects.filter(is_active=True).order_by(
                        "-sort_number", "pk"
                    ),
                    to_attr="files_list",
                ),
                Prefetch(
                    "practices",
                    queryset=Practice.objects.filter(is_active=True).order_by(
                        "-sort_number", "-pk"
                    ),
                    to_attr="practices_list",
                ),
            )
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        section = self.object
        teacher = self.request.teacher

        ctx["articles"] = getattr(section, "articles_list", [])
        ctx["files"] = getattr(section, "files_list", [])
        ctx["practices"] = getattr(section, "practices_list", [])

        # کلاس آنلاین مربوط به این کلاس
        live = (
            LiveClass.objects.filter(is_active=True, klass=section.klass)
            .select_related("server")
            .first()
        )

        # گزارش مربوط به همین جلسه (section) + همین live
        live_report = None
        if live:
            live_report = (
                LiveClassReport.objects.filter(
                    live_class=live,
                    section=section,
                )
                .select_related("live_class", "section")
                .first()
            )

        ctx["live"] = live
        ctx["live_report"] = live_report
        ctx["has_live"] = live is not None
        ctx["can_manage_live"] = bool(getattr(teacher, "can_start_live_class", False))
        ctx["has_live_now"] = bool(live and live.status == LiveClass.Status.LIVE)

        return ctx

# ══════════════════════════════════════════════════════════
# کلاس‌ها
# ══════════════════════════════════════════════════════════

def _get_teacher_section(teacher, pk):
    return get_object_or_404(
        _teacher_sections(teacher).select_related("klass"),
        pk=pk,
    )


# ══════════════════════════════════════════════════════════
# جلسات (Section)
# ══════════════════════════════════════════════════════════

class ClassListView(TeacherMixin, ListView):
    """لیست کلاس‌های معلم"""
    permission_field = "ok"
    template_name = "teacher/class/list.html"
    context_object_name = "classes"
    paginate_by = 20

    def get_queryset(self):
        return (
            _teacher_classes(self.request.teacher)
            .select_related("grade", "major", "lesson", "school")
            .annotate(
                sections_count=Count(
                    "sections",
                    filter=Q(sections__is_active=True),
                    distinct=True,
                ),
                students_count=Count("student", distinct=True),
            )
            .order_by("-sort_number", "-pk")
        )


class SectionListView(TeacherMixin, ListView):
    permission_field = "ok"
    template_name = "teacher/class/sections.html"
    context_object_name = "sections"

    def get_queryset(self):
        self.klass = _get_teacher_class(self.request.teacher, self.kwargs["pk"])
        return (
            Section.objects.filter(klass=self.klass, is_active=True)
            .annotate(
                articles_count=Count("article", filter=Q(article__is_active=True), distinct=True),
                files_count=Count("file", filter=Q(file__is_active=True), distinct=True),
                practices_count=Count("practices", filter=Q(practices__is_active=True), distinct=True),
            )
            .order_by("-sort_number", "pk")
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["klass"] = self.klass

        live_qs = (
            LiveClass.objects.filter(is_active=True, klass=self.klass)
            .select_related("server")
            .prefetch_related(
                Prefetch(
                    "report",
                    queryset=LiveClassReport.objects.all(),
                    to_attr="report_obj",
                )
            )
            .order_by("-pk")
        )
        live_list = list(live_qs)

        ctx["live_classes"] = live_list
        ctx["has_live"] = bool(live_list)
        ctx["can_manage_live"] = bool(getattr(self.request.teacher, "can_start_live_class", False))
        ctx["has_live_now"] = any(live.status == LiveClass.Status.LIVE for live in live_list)

        first_live = next(
            (live for live in live_list if live.status == LiveClass.Status.LIVE),
            live_list[0] if live_list else None,
        )
        ctx["first_live"] = first_live

        # reports that belong to each live session
        ctx["live_reports"] = [
            getattr(live, "report_obj", None)
            for live in live_list
            if getattr(live, "report_obj", None)
        ]
        return ctx


class SectionCreateView(TeacherMixin, CreateView):
    permission_field = "can_add_class_section"
    model = Section
    form_class = SectionForm
    template_name = "teacher/class/section_form.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["klass"] = _get_teacher_class(self.request.teacher, self.kwargs["pk"])
        ctx["page_title"] = "افزودن جلسه"
        ctx["is_update"] = False
        return ctx

    def form_valid(self, form):
        self.klass = _get_teacher_class(self.request.teacher, self.kwargs["pk"])
        form.instance.klass = self.klass
        messages.success(self.request, "جلسه ثبت شد.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("teacher:class-sections", kwargs={"pk": self.klass.pk})


class SectionUpdateView(TeacherMixin, UpdateView):
    permission_field = "can_add_class_section"
    model = Section
    form_class = SectionForm
    template_name = "teacher/class/section_form.html"
    context_object_name = "section"

    def get_queryset(self):
        return _teacher_sections(self.request.teacher)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["klass"] = self.object.klass
        ctx["page_title"] = "ویرایش جلسه"
        ctx["is_update"] = True
        return ctx

    def form_valid(self, form):
        messages.success(self.request, "جلسه بروزرسانی شد.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("teacher:class-sections", kwargs={"pk": self.object.klass_id})

# ══════════════════════════════════════════════════════════
# مقاله کلاسی
# ══════════════════════════════════════════════════════════

class ArticleCreateView(TeacherMixin, CreateView):
    permission_field = "can_add_class_article"
    model = ClassArticle
    form_class = ClassArticleForm
    template_name = "teacher/class/article_form.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["section"] = _get_teacher_section(
            self.request.teacher, self.kwargs["section_id"]
        )
        ctx["page_title"] = "افزودن مقاله"
        ctx["is_update"] = False
        return ctx

    def form_valid(self, form):
        self.section = _get_teacher_section(
            self.request.teacher, self.kwargs["section_id"]
        )
        form.instance.section = self.section
        messages.success(self.request, "مقاله ثبت شد.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("teacher:section-detail", kwargs={"pk": self.section.pk})


class ArticleUpdateView(TeacherMixin, UpdateView):
    permission_field = "can_add_class_article"
    model = ClassArticle
    form_class = ClassArticleForm
    template_name = "teacher/class/article_form.html"
    context_object_name = "article"

    def get_queryset(self):
        return ClassArticle.objects.filter(
            is_active=True,
            section__klass__teacher=self.request.teacher,
            section__is_active=True,
        ).select_related("section")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["section"] = self.object.section
        ctx["page_title"] = "ویرایش مقاله"
        ctx["is_update"] = True
        return ctx

    def form_valid(self, form):
        messages.success(self.request, "مقاله بروزرسانی شد.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("teacher:section-detail", kwargs={"pk": self.object.section_id})


class ArticleDeleteView(TeacherMixin, DeleteView):
    permission_field = "can_add_class_article"
    model = ClassArticle
    template_name = "teacher/class/confirm_delete.html"
    context_object_name = "object"

    def get_queryset(self):
        return ClassArticle.objects.filter(
            is_active=True,
            section__klass__teacher=self.request.teacher,
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["object_label"] = f"مقاله «{self.object.name}»"
        ctx["back_url"] = reverse(
            "teacher:section-detail", kwargs={"pk": self.object.section_id}
        )
        return ctx

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        sid = self.object.section_id
        self.object.is_active = False
        self.object.save(update_fields=["is_active"])
        messages.success(request, "مقاله حذف شد.")
        return HttpResponseRedirect(
            reverse("teacher:section-detail", kwargs={"pk": sid})
        )

    def form_valid(self, form):
        return self.delete(self.request)


# ══════════════════════════════════════════════════════════
# فایل کلاسی
# ══════════════════════════════════════════════════════════

class FileCreateView(TeacherMixin, CreateView):
    permission_field = "can_add_class_file"
    model = ClassFile
    form_class = ClassFileForm
    template_name = "teacher/class/file_form.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["section"] = _get_teacher_section(
            self.request.teacher, self.kwargs["section_id"]
        )
        ctx["page_title"] = "افزودن فایل"
        ctx["is_update"] = False
        return ctx

    def form_valid(self, form):
        self.section = _get_teacher_section(
            self.request.teacher, self.kwargs["section_id"]
        )
        form.instance.section = self.section
        messages.success(self.request, "فایل ثبت شد.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("teacher:section-detail", kwargs={"pk": self.section.pk})


class FileUpdateView(TeacherMixin, UpdateView):
    permission_field = "can_add_class_file"
    model = ClassFile
    form_class = ClassFileForm
    template_name = "teacher/class/file_form.html"
    context_object_name = "class_file"

    def get_queryset(self):
        return ClassFile.objects.filter(
            is_active=True,
            section__klass__teacher=self.request.teacher,
            section__is_active=True,
        ).select_related("section")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["section"] = self.object.section
        ctx["page_title"] = "ویرایش فایل"
        ctx["is_update"] = True
        return ctx

    def form_valid(self, form):
        messages.success(self.request, "فایل بروزرسانی شد.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("teacher:section-detail", kwargs={"pk": self.object.section_id})


class FileDeleteView(TeacherMixin, DeleteView):
    permission_field = "can_add_class_file"
    model = ClassFile
    template_name = "teacher/class/confirm_delete.html"
    context_object_name = "object"

    def get_queryset(self):
        return ClassFile.objects.filter(
            is_active=True,
            section__klass__teacher=self.request.teacher,
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["object_label"] = f"فایل «{self.object.name}»"
        ctx["back_url"] = reverse(
            "teacher:section-detail", kwargs={"pk": self.object.section_id}
        )
        return ctx

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        sid = self.object.section_id
        self.object.is_active = False
        self.object.save(update_fields=["is_active"])
        messages.success(request, "فایل حذف شد.")
        return HttpResponseRedirect(
            reverse("teacher:section-detail", kwargs={"pk": sid})
        )

    def form_valid(self, form):
        return self.delete(self.request)


# ══════════════════════════════════════════════════════════
# درخواست تشکیل کلاس آنلاین
# ══════════════════════════════════════════════════════════

class LiveRequestListView(TeacherMixin, ListView):
    permission_field = "can_start_live_class"
    template_name = "teacher/class/live_request_list.html"
    context_object_name = "items"
    paginate_by = 20

    def get_queryset(self):
        return (
            LiveClassRequest.objects.filter(
                teacher=self.request.teacher,
                is_active=True,
            )
            .order_by("-pk")
        )


class LiveRequestCreateView(TeacherMixin, CreateView):
    permission_field = "can_start_live_class"
    model = LiveClassRequest
    form_class = LiveClassRequestForm
    template_name = "teacher/class/live_request_form.html"
    success_url = reverse_lazy("teacher:live-request-list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["teacher"] = self.request.teacher
        return kwargs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["page_title"] = "درخواست تشکیل کلاس آنلاین"
        ctx["is_update"] = False
        return ctx

    def form_valid(self, form):
        form.instance.teacher = self.request.teacher
        form.instance.status = LiveClassRequest.Status.PENDING
        messages.success(self.request, "درخواست ثبت شد و در انتظار بررسی است.")
        return super().form_valid(form)


class LiveRequestUpdateView(TeacherMixin, UpdateView):
    permission_field = "can_start_live_class"
    model = LiveClassRequest
    form_class = LiveClassRequestForm
    template_name = "teacher/class/live_request_form.html"
    context_object_name = "live_request"
    success_url = reverse_lazy("teacher:live-request-list")

    def get_queryset(self):
        return LiveClassRequest.objects.filter(
            teacher=self.request.teacher,
            is_active=True,
            status=LiveClassRequest.Status.PENDING,
        )

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["teacher"] = self.request.teacher
        return kwargs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["page_title"] = "ویرایش درخواست"
        ctx["is_update"] = True
        return ctx

    def form_valid(self, form):
        messages.success(self.request, "درخواست بروزرسانی شد.")
        return super().form_valid(form)


class LiveRequestDeleteView(TeacherMixin, DeleteView):
    permission_field = "can_start_live_class"
    model = LiveClassRequest
    template_name = "teacher/class/confirm_delete.html"
    success_url = reverse_lazy("teacher:live-request-list")
    context_object_name = "object"

    def get_queryset(self):
        return LiveClassRequest.objects.filter(
            teacher=self.request.teacher,
            is_active=True,
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["object_label"] = f"درخواست «{self.object.title}»"
        ctx["back_url"] = reverse("teacher:live-request-list")
        return ctx

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.is_active = False
        self.object.save(update_fields=["is_active"])
        messages.success(request, "درخواست حذف شد.")
        return HttpResponseRedirect(self.get_success_url())

    def form_valid(self, form):
        return self.delete(self.request)


class LiveRequestDetailView(TeacherMixin, DetailView):
    permission_field = "can_start_live_class"
    model = LiveClassRequest
    template_name = "teacher/class/live_request_detail.html"
    context_object_name = "live_request"

    def get_queryset(self):
        return LiveClassRequest.objects.filter(
            teacher=self.request.teacher,
            is_active=True,
        )



class LiveClassReportCreateView(TeacherMixin, CreateView):
    """آپلود گزارش برای یک کلاس آنلاین (متعلق به یک جلسه مشخص)"""
    permission_field = "can_start_live_class"
    model = LiveClassReport
    form_class = LiveClassReportForm
    template_name = "teacher/class/live_report_form.html"

    def get_live(self):
        return get_object_or_404(
            LiveClass.objects.select_related("klass"),
            pk=self.kwargs["live_pk"],
            is_active=True,
            klass__teacher=self.request.teacher,
            klass__is_active=True,
        )

    def get_section(self):
        return get_object_or_404(
            Section.objects.filter(
                is_active=True,
                klass__teacher=self.request.teacher,
                klass__is_active=True,
            ),
            pk=self.kwargs["section_id"],
        )

    def get_existing_report(self, live=None, section_id=None):
        live = live or self.get_live()
        section_id = section_id or self.kwargs["section_id"]
        return LiveClassReport.objects.filter(
            live_class=live,
            section_id=section_id,
        ).first()

    def get(self, request, *args, **kwargs):
        self.live = self.get_live()
        existing = self.get_existing_report(live=self.live)
        if existing:
            return redirect("teacher:live-report-update", pk=existing.pk)
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.live = self.get_live()
        existing = self.get_existing_report(live=self.live)
        if existing:
            return redirect("teacher:live-report-update", pk=existing.pk)
        return super().post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        live = getattr(self, "live", None) or self.get_live()
        section = self.get_section()
        ctx["live"] = live
        ctx["section"] = section
        ctx["klass"] = live.klass
        ctx["page_title"] = "ثبت گزارش کلاس آنلاین"
        ctx["is_update"] = False
        return ctx

    def form_valid(self, form):
        live = self.get_live()
        section = self.get_section()

        existing = self.get_existing_report(live=live, section_id=section.pk)
        if existing:
            return redirect("teacher:live-report-update", pk=existing.pk)

        form.instance.live_class = live
        form.instance.section = section
        messages.success(self.request, "گزارش جلسه ثبت شد.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            "teacher:section-detail",
            kwargs={"pk": self.kwargs["section_id"]},
        )

class LiveClassReportUpdateView(TeacherMixin, UpdateView):
    """ویرایش گزارش یک کلاس آنلاین"""
    permission_field = "can_start_live_class"
    model = LiveClassReport
    form_class = LiveClassReportForm
    template_name = "teacher/class/live_report_form.html"
    context_object_name = "report"

    def get_queryset(self):
        return (
            LiveClassReport.objects.filter(
                live_class__is_active=True,
                live_class__klass__teacher=self.request.teacher,
                live_class__klass__is_active=True,
                section__is_active=True,
                section__klass__teacher=self.request.teacher,
            )
            .select_related(
                "live_class",
                "live_class__klass",
                "live_class__server",
                "section",
                "section__klass",
            )
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["live"] = self.object.live_class
        ctx["section"] = self.object.section
        ctx["klass"] = self.object.live_class.klass
        ctx["page_title"] = "ویرایش گزارش کلاس آنلاین"
        ctx["is_update"] = True
        return ctx

    def form_valid(self, form):
        messages.success(self.request, "گزارش جلسه بروزرسانی شد.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            "teacher:section-detail",
            kwargs={"pk": self.object.section_id},
        )


# ══════════════════════════════════════════════════════════
# ورود معلم به کلاس آنلاین
# ══════════════════════════════════════════════════════════

class LiveJoinView(TeacherMixin, View):
    permission_field = "can_start_live_class"

    def get(self, request, pk):
        live = get_object_or_404(
            LiveClass.objects.select_related(
                "server", "klass", "klass__teacher", "klass__teacher__user"
            ),
            pk=pk,
            is_active=True,
            klass__teacher=request.teacher,
            klass__is_active=True,
        )

        # ورود = خودکار وضعیت را LIVE کن
        if live.status != LiveClass.Status.LIVE:
            live.status = LiveClass.Status.LIVE
            live.save(update_fields=["status"])

        url = live.teacher_meeting_url
        if not url:
            messages.warning(request, "لینک ورود ساخته نشد. سرور را بررسی کنید.")
            return redirect("teacher:class-sections", pk=live.klass_id)

        return redirect(url)


class LiveClassListView(TeacherMixin, ListView):
    permission_field = "can_start_live_class"
    template_name = "teacher/class/live_list.html"
    context_object_name = "items"

    def get_queryset(self):
        return (
            LiveClass.objects.filter(
                is_active=True,
                klass__teacher=self.request.teacher,
                klass__is_active=True,
            )
            .select_related("klass", "server")
            .prefetch_related(
                Prefetch(
                    "report",
                    queryset=LiveClassReport.objects.all(),
                    to_attr="report_obj",
                )
            )
            .order_by("-pk")
        )


class LiveClassUpdateView(TeacherMixin, UpdateView):
    """ویرایش کلاس آنلاین"""
    permission_field = "can_start_live_class"
    model = LiveClass
    form_class = LiveClassForm
    template_name = "teacher/class/live_form.html"
    context_object_name = "live"

    def get_queryset(self):
        return LiveClass.objects.filter(
            is_active=True,
            klass__teacher=self.request.teacher,
            klass__is_active=True,
        ).select_related("klass", "server")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["klass"] = self.object.klass
        ctx["page_title"] = "ویرایش کلاس آنلاین"
        ctx["is_update"] = True
        return ctx

    def form_valid(self, form):
        messages.success(self.request, "کلاس آنلاین بروزرسانی شد.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("teacher:class-sections", kwargs={"pk": self.object.klass_id})


class LiveClassSetStatusView(TeacherMixin, View):
    """تغییر وضعیت کلاس آنلاین"""
    permission_field = "can_start_live_class"

    ALLOWED = {
        LiveClass.Status.LIVE,
        LiveClass.Status.COMPLETED,
        LiveClass.Status.CANCELLED,
        LiveClass.Status.SCHEDULED,
    }

    def post(self, request, pk):
        live = get_object_or_404(
            LiveClass.objects.select_related("klass"),
            pk=pk,
            is_active=True,
            klass__teacher=request.teacher,
            klass__is_active=True,
        )
        status = request.POST.get("status")
        if status not in self.ALLOWED:
            messages.error(request, "وضعیت نامعتبر است.")
            return redirect("teacher:class-sections", pk=live.klass_id)

        live.status = status
        live.save(update_fields=["status"])
        messages.success(request, f"وضعیت شد: {live.get_status_display()}")
        return redirect("teacher:class-sections", pk=live.klass_id)