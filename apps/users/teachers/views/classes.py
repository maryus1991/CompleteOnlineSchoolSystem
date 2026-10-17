from django.contrib import messages
from django.db.models import Count, Prefetch, Q
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from apps.classes.models import Class
from apps.content.models import ClassArticle, ClassFile, Section
from apps.live_classes.models import LiveClass, LiveClassRequest
from apps.practice.models import Practice
from apps.users.teachers.forms.classes import (
    ClassArticleForm,
    ClassFileForm,
    LiveClassRequestForm,
    SectionForm,
)
from apps.users.teachers.mixins import TeacherMixin


# ── helpers ──────────────────────────────────────────────

def _teacher_classes(teacher):
    return Class.objects.filter(teacher=teacher, is_active=True)


def _teacher_sections(teacher):
    return Section.objects.filter(
        is_active=True,
        klass__teacher=teacher,
        klass__is_active=True,
    )


def _get_teacher_class(teacher, pk):
    return get_object_or_404(_teacher_classes(teacher), pk=pk)


def _get_teacher_section(teacher, pk):
    return get_object_or_404(
        _teacher_sections(teacher).select_related("klass"),
        pk=pk,
    )


# ══════════════════════════════════════════════════════════
# کلاس‌ها
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


# ══════════════════════════════════════════════════════════
# جلسات (Section)
# ══════════════════════════════════════════════════════════

class SectionListView(TeacherMixin, ListView):
    """لیست جلسات یک کلاس + لینک ورود به لایو"""

    permission_field = "ok"
    template_name = "teacher/class/sections.html"
    context_object_name = "sections"

    def dispatch(self, request, *args, **kwargs):
        self.klass = _get_teacher_class(request.teacher, kwargs["pk"])
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return (
            Section.objects.filter(klass=self.klass, is_active=True)
            .annotate(
                articles_count=Count("article", filter=Q(article__is_active=True), distinct=True),
                files_count=Count("file", filter=Q(file__is_active=True), distinct=True),
                practices_count=Count("practices", filter=Q(practices__is_active=True), distinct=True),
            )
            .prefetch_related(
                Prefetch(
                    "live",
                    queryset=LiveClass.objects.filter(is_active=True).select_related("server"),
                    to_attr="live_list",
                )
            )
            .order_by("-sort_number", "pk")
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["klass"] = self.klass
        return ctx


class SectionCreateView(TeacherMixin, CreateView):
    permission_field = "can_add_class_section"
    model = Section
    form_class = SectionForm
    template_name = "teacher/class/section_form.html"

    def dispatch(self, request, *args, **kwargs):
        self.klass = _get_teacher_class(request.teacher, kwargs["pk"])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["klass"] = self.klass
        ctx["page_title"] = "افزودن جلسه"
        ctx["is_update"] = False
        return ctx

    def form_valid(self, form):
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
        ctx["back_url"] = reverse("teacher:class-sections", kwargs={"pk": self.object.klass_id})
        return ctx

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        klass_id = self.object.klass_id
        self.object.is_active = False
        self.object.save(update_fields=["is_active"])
        messages.success(request, "جلسه حذف شد.")
        return HttpResponseRedirect(reverse("teacher:class-sections", kwargs={"pk": klass_id}))

    def form_valid(self, form):
        return self.delete(self.request)


# ══════════════════════════════════════════════════════════
# جزئیات جلسه (مقاله / فایل / تمرین / ورود لایو)
# ══════════════════════════════════════════════════════════

class SectionDetailView(TeacherMixin, DetailView):
    permission_field = "ok"
    model = Section
    template_name = "teacher/class/section_detail.html"
    context_object_name = "section"

    def get_queryset(self):
        return (
            _teacher_sections(self.request.teacher)
            .select_related("klass")
            .prefetch_related(
                Prefetch(
                    "article",
                    queryset=ClassArticle.objects.filter(is_active=True).order_by("-sort_number", "pk"),
                    to_attr="articles_list",
                ),
                Prefetch(
                    "file",
                    queryset=ClassFile.objects.filter(is_active=True).order_by("-sort_number", "pk"),
                    to_attr="files_list",
                ),
                Prefetch(
                    "practices",
                    queryset=Practice.objects.filter(is_active=True).order_by("-sort_number", "-pk"),
                    to_attr="practices_list",
                ),
                Prefetch(
                    "live",
                    queryset=LiveClass.objects.filter(is_active=True).select_related("server"),
                    to_attr="live_list",
                ),
            )
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        section = self.object
        ctx["articles"] = getattr(section, "articles_list", [])
        ctx["files"] = getattr(section, "files_list", [])
        ctx["practices"] = getattr(section, "practices_list", [])
        live_list = getattr(section, "live_list", [])
        ctx["live_classes"] = live_list
        # لینک ورود معلم به اولین جلسه لایو در دسترس
        join_url = None
        for live in live_list:
            url = live.teacher_meeting_url
            if url:
                join_url = url
                break
        ctx["teacher_join_url"] = join_url
        return ctx


# ══════════════════════════════════════════════════════════
# مقاله کلاسی
# ══════════════════════════════════════════════════════════

class ArticleCreateView(TeacherMixin, CreateView):
    permission_field = "can_add_class_article"
    model = ClassArticle
    form_class = ClassArticleForm
    template_name = "teacher/class/article_form.html"

    def dispatch(self, request, *args, **kwargs):
        self.section = _get_teacher_section(request.teacher, kwargs["section_id"])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["section"] = self.section
        ctx["page_title"] = "افزودن مقاله"
        ctx["is_update"] = False
        return ctx

    def form_valid(self, form):
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
        ctx["back_url"] = reverse("teacher:section-detail", kwargs={"pk": self.object.section_id})
        return ctx

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        sid = self.object.section_id
        self.object.is_active = False
        self.object.save(update_fields=["is_active"])
        messages.success(request, "مقاله حذف شد.")
        return HttpResponseRedirect(reverse("teacher:section-detail", kwargs={"pk": sid}))

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

    def dispatch(self, request, *args, **kwargs):
        self.section = _get_teacher_section(request.teacher, kwargs["section_id"])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["section"] = self.section
        ctx["page_title"] = "افزودن فایل"
        ctx["is_update"] = False
        return ctx

    def form_valid(self, form):
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
        ctx["back_url"] = reverse("teacher:section-detail", kwargs={"pk": self.object.section_id})
        return ctx

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        sid = self.object.section_id
        self.object.is_active = False
        self.object.save(update_fields=["is_active"])
        messages.success(request, "فایل حذف شد.")
        return HttpResponseRedirect(reverse("teacher:section-detail", kwargs={"pk": sid}))

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
            .select_related("section", "section__klass")
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
        section = form.cleaned_data["section"]
        if section.klass.teacher_id != self.request.teacher.pk:
            messages.error(self.request, "دسترسی به این جلسه مجاز نیست.")
            return self.form_invalid(form)
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
        ).select_related("section", "section__klass")


# ══════════════════════════════════════════════════════════
# ورود معلم به کلاس آنلاین
# ══════════════════════════════════════════════════════════

class LiveJoinView(TeacherMixin, View):
    """هدایت معلم به لینک کلاس آنلاین (teacher_meeting_url)"""

    permission_field = "can_start_live_class"

    def get(self, request, pk):
        live = get_object_or_404(
            LiveClass.objects.select_related(
                "server",
                "section",
                "section__klass",
            ),
            pk=pk,
            is_active=True,
            section__klass__teacher=request.teacher,
            section__is_active=True,
        )
        url = live.teacher_meeting_url
        if not url:
            messages.warning(
                request,
                "کلاس آنلاین در حال حاضر در دسترس نیست (باید وضعیت «در حال برگزاری» باشد).",
            )
            return redirect("teacher:section-detail", pk=live.section_id)
        return redirect(url)


class LiveClassListView(TeacherMixin, ListView):
    """لیست کلاس‌های آنلاین مرتبط با معلم"""

    permission_field = "can_start_live_class"
    template_name = "teacher/class/live_list.html"
    context_object_name = "items"

    def get_queryset(self):
        return (
            LiveClass.objects.filter(
                is_active=True,
                section__klass__teacher=self.request.teacher,
                section__is_active=True,
                section__klass__is_active=True,
            )
            .select_related("section", "section__klass", "server")
            .order_by("-pk")
        )
