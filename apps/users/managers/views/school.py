from django.contrib import messages
from django.db.models import Count, Q
from django.shortcuts import redirect
from django.views.generic import TemplateView

from apps.categories.models import GradeCategories, LessonCategories, MajorCategories
from apps.users.managers.forms.school import AcademicCategoryQuickForm, SchoolInfoForm
from apps.users.managers.mixins import ManagerMixin


class SchoolInfoUpdateView(ManagerMixin, TemplateView):
    template_name = "manager/school/school_info.html"
    permission_field = "can_manage_school_settings"


    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        school = self.get_school()
        if "form" not in ctx:
            ctx["form"] = SchoolInfoForm(instance=school)


        # if "category_form" not in ctx:
        #     ctx["category_form"] = AcademicCategoryQuickForm()

        ctx["grades"] = (
            GradeCategories.objects.filter(is_active=True)
            .annotate(
                school_students_count=Count(
                    "student",
                    filter=Q(student__school=school, student__is_active=True),
                    distinct=True,
                ),
                school_classes_count=Count(
                    "classes",
                    filter=Q(classes__school=school, classes__is_active=True),
                    distinct=True,
                ),
            )
            .order_by("-sort_number", "-pk")
        )
        ctx["majors"] = (
            MajorCategories.objects.filter(is_active=True)
            .annotate(
                school_students_count=Count(
                    "student",
                    filter=Q(student__school=school, student__is_active=True),
                    distinct=True,
                ),
                school_classes_count=Count(
                    "classes",
                    filter=Q(classes__school=school, classes__is_active=True),
                    distinct=True,
                ),
            )
            .order_by("-sort_number", "-pk")
        )
        ctx["lessons"] = (
            LessonCategories.objects.filter(is_active=True)
            .annotate(
                school_classes_count=Count(
                    "classes",
                    filter=Q(classes__school=school, classes__is_active=True),
                    distinct=True,
                ),
                school_exams_count=Count(
                    "exam",
                    filter=Q(exam__school=school, exam__is_active=True),
                    distinct=True,
                ),
            )
            .order_by("-sort_number", "-pk")
        )
        return ctx

    def post(self, request, *args, **kwargs):
        school = self.get_school()
        # action = request.POST.get("action", "update_school")
        # if action == "add_category":
        #     c_form = AcademicCategoryQuickForm(request.POST)
        #     if c_form.is_valid():
        #         c_type = c_form.cleaned_data["category_type"]
        #         name = c_form.cleaned_data["name"].strip()
        #         sort_num = c_form.cleaned_data.get("sort_number") or 1
        #         model_map = {
        #             "grade": GradeCategories,
        #             "major": MajorCategories,
        #             "lesson": LessonCategories,
        #         }
        #         model_cls = model_map[c_type]
        #         obj, created = model_cls.objects.get_or_create(
        #             name=name,
        #             defaults={"sort_number": sort_num, "is_active": True},
        #         )
        #         if not obj.is_active:
        #             obj.is_active = True
        #             obj.save(update_fields=["is_active"])
        #         messages.success(
        #             request,
        #             f"دسته‌بندی آموزشی «{name}» با موفقیت ثبت/فعال شد.",
        #         )
        #         return redirect("manager:school-info")
        #     return self.render_to_response(
        #         self.get_context_data(category_form=c_form)
        #     )

        form = SchoolInfoForm(request.POST, instance=school)
        if form.is_valid():
            form.save()
            messages.success(request, "اطلاعات پایه مدرسه با موفقیت بروزرسانی شد.")
            return redirect("manager:school-info")
        messages.error(request, "لطفاً اطلاعات واردشده را بررسی کنید.")
        return self.render_to_response(self.get_context_data(form=form))
