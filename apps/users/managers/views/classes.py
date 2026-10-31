from django.contrib import messages
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.views.generic import ListView, TemplateView

from apps.categories.models import GradeCategories, LessonCategories, MajorCategories
from apps.content.models import ClassArticle, ClassFile, Section
from apps.users.managers.forms.classes import (
    ManagerClassArticleForm,
    ManagerClassFileForm,
    ManagerClassForm,
    ManagerSectionForm,
)
from apps.users.managers.mixins import ManagerMixin


class ClassListView(ManagerMixin, ListView):
    template_name = "manager/classes/class_list.html"
    context_object_name = "classes"
    paginate_by = 20
    permission_field = "can_manage_classes"

    def get_queryset(self):
        qs = (
            self.get_school_classes_queryset()
            .annotate(
                students_count=Count("student", distinct=True),
                sections_count=Count("sections", distinct=True),
                live_count=Count("live", distinct=True),
            )
            .order_by("-sort_number", "-pk")
        )
        q = (self.request.GET.get("q") or "").strip()
        grade_id = (self.request.GET.get("grade") or "").strip()
        major_id = (self.request.GET.get("major") or "").strip()
        lesson_id = (self.request.GET.get("lesson") or "").strip()
        teacher_id = (self.request.GET.get("teacher") or "").strip()
        status = (self.request.GET.get("status") or "").strip()

        if q:
            qs = qs.filter(
                Q(name__icontains=q)
                | Q(summery__icontains=q)
                | Q(teacher__user__first_name__icontains=q)
                | Q(teacher__user__last_name__icontains=q)
            )
        if grade_id.isdigit():
            qs = qs.filter(grade_id=int(grade_id))
        if major_id.isdigit():
            qs = qs.filter(major_id=int(major_id))
        if lesson_id.isdigit():
            qs = qs.filter(lesson_id=int(lesson_id))
        if teacher_id.isdigit():
            qs = qs.filter(teacher_id=int(teacher_id))
        if status == "active":
            qs = qs.filter(is_active=True)
        elif status == "inactive":
            qs = qs.filter(is_active=False)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["grades"] = GradeCategories.objects.filter(is_active=True)
        ctx["majors"] = MajorCategories.objects.filter(is_active=True)
        ctx["lessons"] = LessonCategories.objects.filter(is_active=True)
        ctx["teachers"] = self.get_school_teachers_queryset().filter(is_active=True)
        return ctx


class ClassCreateView(ManagerMixin, TemplateView):
    template_name = "manager/classes/class_form.html"
    permission_field = "can_manage_classes"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["is_edit"] = False
        if "form" not in ctx:
            ctx["form"] = ManagerClassForm(school=self.get_school())
        return ctx

    def post(self, request, *args, **kwargs):
        school = self.get_school()
        form = ManagerClassForm(request.POST, request.FILES, school=school)
        if form.is_valid():
            klass = form.save(commit=False)
            klass.school = school
            klass.save()
            form.save_m2m()
            messages.success(request, f"کلاس «{klass.name}» با موفقیت ایجاد شد.")
            return redirect("manager:class-list")
        messages.error(request, "لطفاً اطلاعات فرم ایجاد کلاس را بررسی کنید.")
        return self.render_to_response(self.get_context_data(form=form))


class ClassUpdateView(ManagerMixin, TemplateView):
    template_name = "manager/classes/class_form.html"
    permission_field = "can_manage_classes"

    def get_class_obj(self):
        return get_object_or_404(
            self.get_school_classes_queryset(), pk=self.kwargs["pk"]
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        klass = self.get_class_obj()
        ctx["class_obj"] = klass
        ctx["is_edit"] = True
        if "form" not in ctx:
            ctx["form"] = ManagerClassForm(instance=klass, school=self.get_school())
        return ctx

    def post(self, request, *args, **kwargs):
        klass = self.get_class_obj()
        school = self.get_school()
        form = ManagerClassForm(
            request.POST, request.FILES, instance=klass, school=school
        )
        if form.is_valid():
            updated = form.save(commit=False)
            if not updated.school_id:
                updated.school = school
            updated.save()
            form.save_m2m()
            messages.success(request, f"کلاس «{updated.name}» با موفقیت ویرایش شد.")
            return redirect("manager:class-list")
        messages.error(request, "لطفاً اطلاعات فرم ویرایش کلاس را بررسی کنید.")
        return self.render_to_response(self.get_context_data(form=form))


class ClassToggleActiveView(ManagerMixin, View):
    permission_field = "can_manage_classes"

    def post(self, request, pk, *args, **kwargs):
        klass = get_object_or_404(self.get_school_classes_queryset(), pk=pk)
        new_state = self.toggle_object_active(klass)
        status_label = "فعال" if new_state else "غیرفعال"
        messages.info(
            request,
            f"وضعیت کلاس «{klass.name}» به «{status_label}» تغییر یافت (بدون حذف).",
        )
        return redirect(request.META.get("HTTP_REFERER") or "manager:class-list")


# ============================================================
# مدیریت جلسات (Section) و محتوای جلسه (مقاله، فایل، تمرین)
# ============================================================
class SectionManageView(ManagerMixin, TemplateView):
    template_name = "manager/classes/section_manage.html"
    permission_field = "can_manage_classes"

    def get_class_obj(self):
        return get_object_or_404(
            self.get_school_classes_queryset(), pk=self.kwargs["class_pk"]
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        klass = self.get_class_obj()
        ctx["class_obj"] = klass
        ctx["sections"] = (
            Section.objects.filter(klass=klass)
            .prefetch_related("article", "file", "practices")
            .annotate(
                articles_count=Count("article", distinct=True),
                files_count=Count("file", distinct=True),
                practices_count=Count("practices", distinct=True),
            )
            .order_by("-sort_number", "pk")
        )
        if "section_form" not in ctx:
            ctx["section_form"] = ManagerSectionForm(initial={"is_publish": True, "is_active": True})
        if "article_form" not in ctx:
            ctx["article_form"] = ManagerClassArticleForm(initial={"is_active": True})
        if "file_form" not in ctx:
            ctx["file_form"] = ManagerClassFileForm(initial={"is_active": True})
        return ctx

    def post(self, request, *args, **kwargs):
        klass = self.get_class_obj()
        action = request.POST.get("action", "create_section")

        if action == "create_section":
            form = ManagerSectionForm(request.POST)
            if form.is_valid():
                sec = form.save(commit=False)
                sec.klass = klass
                sec.save()
                messages.success(request, f"جلسه «{sec.name}» به کلاس اضافه شد.")
                return redirect("manager:class-sections", class_pk=klass.pk)
            return self.render_to_response(self.get_context_data(section_form=form))

        if action == "update_section":
            sec = get_object_or_404(
                Section, pk=request.POST.get("section_id"), klass=klass
            )
            form = ManagerSectionForm(request.POST, instance=sec)
            if form.is_valid():
                form.save()
                messages.success(request, f"جلسه «{sec.name}» بروزرسانی شد.")
            return redirect("manager:class-sections", class_pk=klass.pk)

        if action == "add_article":
            sec = get_object_or_404(
                Section, pk=request.POST.get("section_id"), klass=klass
            )
            form = ManagerClassArticleForm(request.POST)
            if form.is_valid():
                art = form.save(commit=False)
                art.section = sec
                art.save()
                messages.success(request, f"مقاله آموزشی «{art.name}» به جلسه «{sec.name}» اضافه شد.")
                return redirect("manager:class-sections", class_pk=klass.pk)
            return self.render_to_response(self.get_context_data(article_form=form))

        if action == "add_file":
            sec = get_object_or_404(
                Section, pk=request.POST.get("section_id"), klass=klass
            )
            form = ManagerClassFileForm(request.POST, request.FILES)
            if form.is_valid():
                cfile = form.save(commit=False)
                cfile.section = sec
                cfile.save()
                messages.success(request, f"فایل آموزشی «{cfile.name}» به جلسه «{sec.name}» اضافه شد.")
                return redirect("manager:class-sections", class_pk=klass.pk)
            return self.render_to_response(self.get_context_data(file_form=form))

        return redirect("manager:class-sections", class_pk=klass.pk)


class SectionToggleActiveView(ManagerMixin, View):
    permission_field = "can_manage_classes"

    def post(self, request, pk, *args, **kwargs):
        sec = get_object_or_404(self.get_school_sections_queryset(), pk=pk)
        new_state = self.toggle_object_active(sec)
        status_label = "فعال" if new_state else "غیرفعال"
        messages.info(
            request,
            f"وضعیت جلسه «{sec.name}» به «{status_label}» تغییر یافت.",
        )
        return redirect("manager:class-sections", class_pk=sec.klass_id)


class SectionContentToggleActiveView(ManagerMixin, View):
    permission_field = "can_manage_classes"

    def post(self, request, kind, pk, *args, **kwargs):
        school = self.get_school()
        if kind == "article":
            obj = get_object_or_404(
                ClassArticle.objects.filter(
                    Q(section__klass__school=school)
                    | Q(section__klass__teacher__school=school)
                ),
                pk=pk,
            )
        else:
            obj = get_object_or_404(
                ClassFile.objects.filter(
                    Q(section__klass__school=school)
                    | Q(section__klass__teacher__school=school)
                ),
                pk=pk,
            )
        new_state = self.toggle_object_active(obj)
        status_label = "فعال" if new_state else "غیرفعال"
        messages.info(
            request,
            f"وضعیت محتوای «{obj.name}» به «{status_label}» تغییر یافت.",
        )
        return redirect("manager:class-sections", class_pk=obj.section.klass_id)
