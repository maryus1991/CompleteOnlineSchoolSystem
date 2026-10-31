from django.contrib import messages
from django.db import transaction
from django.db.models import Avg, Count, Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.views.generic import ListView, TemplateView

from apps.categories.models import GradeCategories, MajorCategories
from apps.users.accounts.models import User
from apps.users.advisers.models import Adviser
from apps.users.managers.excel_utils import (
    STUDENT_TEMPLATE_COLUMNS,
    get_student_import_template_bytes,
    validate_and_import_students,
)
from apps.users.managers.forms.users import (
    AdviserPermissionsForm,
    ManagerAdviserForm,
    ManagerStudentForm,
    ManagerTeacherForm,
    StudentBulkImportForm,
    TeacherPermissionsForm,
)
from apps.users.managers.mixins import ManagerMixin
from apps.users.students.models import Student
from apps.users.teachers.models import Teacher


# ============================================================
# مدیریت دانش‌آموزان مدرسه
# ============================================================
class StudentListView(ManagerMixin, ListView):
    template_name = "manager/users/student_list.html"
    context_object_name = "students"
    paginate_by = 25
    permission_field = "can_manage_users"

    def get_queryset(self):
        qs = (
            self.get_school_students_queryset()
            .annotate(
                classes_count=Count("classes", distinct=True),
                exams_count=Count("exam_reports", distinct=True),
                avg_percentage=Avg("exam_reports__percentage"),
            )
            .order_by("-pk")
        )
        q = (self.request.GET.get("q") or "").strip()
        grade_id = (self.request.GET.get("grade") or "").strip()
        major_id = (self.request.GET.get("major") or "").strip()
        adviser_id = (self.request.GET.get("adviser") or "").strip()
        status = (self.request.GET.get("status") or "").strip()

        if q:
            qs = qs.filter(
                Q(user__first_name__icontains=q)
                | Q(user__last_name__icontains=q)
                | Q(user__PhoneNumber=q)
                | Q(user__private_code__icontains=q)
            )
        if grade_id.isdigit():
            qs = qs.filter(grade_id=int(grade_id))
        if major_id.isdigit():
            qs = qs.filter(major_id=int(major_id))
        if adviser_id.isdigit():
            qs = qs.filter(adviser_id=int(adviser_id))
        if status == "active":
            qs = qs.filter(is_active=True)
        elif status == "inactive":
            qs = qs.filter(is_active=False)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["grades"] = GradeCategories.objects.filter(is_active=True)
        ctx["majors"] = MajorCategories.objects.filter(is_active=True)
        ctx["advisers"] = self.get_school_advisers_queryset().filter(is_active=True)
        return ctx


class StudentCreateView(ManagerMixin, TemplateView):
    template_name = "manager/users/student_form.html"
    permission_field = "can_manage_users"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["is_edit"] = False
        if "form" not in ctx:
            ctx["form"] = ManagerStudentForm(
                school=self.get_school(),
                initial={
                    "province": self.get_school().province,
                    "city": self.get_school().city,
                    "is_active": True,
                },
            )
        return ctx

    def post(self, request, *args, **kwargs):
        school = self.get_school()
        form = ManagerStudentForm(request.POST, school=school)
        if not form.is_valid():
            messages.error(request, "لطفاً خطاهای فرم ثبت دانش‌آموز را برطرف کنید.")
            return self.render_to_response(self.get_context_data(form=form))

        data = form.cleaned_data
        raw_pass = (data.get("password") or "").strip() or (
            data.get("private_code") or data["phone_number"][-8:]
        )
        with transaction.atomic():
            user = User.objects.create_user(
                PhoneNumber=data["phone_number"],
                password=raw_pass,
                first_name=data["first_name"],
                last_name=data["last_name"],
                gender=data["gender"],
                type_of_user=User.TypeOfUser.STUDENT,
                private_code=data.get("private_code"),
                is_verified=True,
                is_active=bool(data.get("is_active", True)),
            )
            student = Student(
                user=user,
                school=school,
                grade=data.get("grade"),
                major=data.get("major"),
                adviser=data.get("adviser"),
                province=data.get("province") or school.province,
                city=data.get("city") or school.city,
                parent_phone_number=data.get("parent_phone_number"),
                target_major_rank=data.get("target_major_rank"),
                counseling_notes_summary=data.get("counseling_notes_summary"),
                is_active=bool(data.get("is_active", True)),
            )
            student.full_clean()
            student.save()

        messages.success(request, f"دانش‌آموز «{user.get_full_name()}» با موفقیت به مدرسه اضافه شد.")
        return redirect("manager:student-list")


class StudentUpdateView(ManagerMixin, TemplateView):
    template_name = "manager/users/student_form.html"
    permission_field = "can_manage_users"

    def get_student(self):
        return get_object_or_404(
            self.get_school_students_queryset(), pk=self.kwargs["pk"]
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        student = self.get_student()
        ctx["student_obj"] = student
        ctx["is_edit"] = True
        if "form" not in ctx:
            ctx["form"] = ManagerStudentForm(
                school=self.get_school(),
                student_instance=student,
                initial={
                    "phone_number": str(student.user.PhoneNumber),
                    "first_name": student.user.first_name,
                    "last_name": student.user.last_name,
                    "gender": student.user.gender,
                    "private_code": student.user.private_code,
                    "parent_phone_number": str(student.parent_phone_number or ""),
                    "grade": student.grade_id,
                    "major": student.major_id,
                    "adviser": student.adviser_id,
                    "province": student.province,
                    "city": student.city,
                    "target_major_rank": student.target_major_rank,
                    "counseling_notes_summary": student.counseling_notes_summary,
                    "is_active": student.is_active,
                },
            )
        return ctx

    def post(self, request, *args, **kwargs):
        student = self.get_student()
        school = self.get_school()
        form = ManagerStudentForm(
            request.POST, school=school, student_instance=student
        )
        if not form.is_valid():
            messages.error(request, "لطفاً خطاهای فرم ویرایش دانش‌آموز را بررسی کنید.")
            return self.render_to_response(self.get_context_data(form=form))

        data = form.cleaned_data
        user = student.user
        with transaction.atomic():
            user.PhoneNumber = data["phone_number"]
            user.first_name = data["first_name"]
            user.last_name = data["last_name"]
            user.gender = data["gender"]
            user.private_code = data.get("private_code")
            user.is_active = bool(data.get("is_active", False))
            if data.get("password"):
                user.set_password(data["password"])
            user.save()

            student.grade = data.get("grade")
            student.major = data.get("major")
            student.adviser = data.get("adviser")
            student.province = data.get("province")
            student.city = data.get("city")
            student.parent_phone_number = data.get("parent_phone_number")
            student.target_major_rank = data.get("target_major_rank")
            student.counseling_notes_summary = data.get("counseling_notes_summary")
            student.is_active = bool(data.get("is_active", False))
            student.full_clean()
            student.save()

        messages.success(request, "اطلاعات دانش‌آموز با موفقیت ویرایش شد.")
        return redirect("manager:student-list")


class StudentToggleActiveView(ManagerMixin, View):
    permission_field = "can_manage_users"

    def post(self, request, pk, *args, **kwargs):
        student = get_object_or_404(self.get_school_students_queryset(), pk=pk)
        new_state = self.toggle_object_active(student, sync_user=True)
        status_label = "فعال" if new_state else "غیرفعال"
        messages.info(
            request,
            f"وضعیت حساب دانش‌آموز «{student}» به «{status_label}» تغییر یافت (بدون حذف).",
        )
        return redirect(request.META.get("HTTP_REFERER") or "manager:student-list")


class StudentExcelTemplateDownloadView(ManagerMixin, View):
    permission_field = "can_manage_users"

    def get(self, request, *args, **kwargs):
        fmt = (request.GET.get("format") or "xlsx").lower()
        content, content_type, filename = get_student_import_template_bytes(fmt=fmt)
        response = HttpResponse(content, content_type=content_type)
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response


class StudentBulkImportView(ManagerMixin, TemplateView):
    template_name = "manager/users/student_import.html"
    permission_field = "can_manage_users"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["template_columns"] = STUDENT_TEMPLATE_COLUMNS
        ctx["available_grades"] = GradeCategories.objects.filter(is_active=True)
        ctx["available_majors"] = MajorCategories.objects.filter(is_active=True)
        if "form" not in ctx:
            ctx["form"] = StudentBulkImportForm(school=self.get_school())
        return ctx

    def post(self, request, *args, **kwargs):
        school = self.get_school()
        form = StudentBulkImportForm(request.POST, request.FILES, school=school)
        if not form.is_valid():
            messages.error(request, "لطفاً فایل اکسل یا CSV معتبر انتخاب کنید.")
            return self.render_to_response(self.get_context_data(form=form))

        try:
            result = validate_and_import_students(
                uploaded_file=form.cleaned_data["file"],
                school=school,
                default_adviser=form.cleaned_data.get("default_adviser"),
            )

        except Exception as e:
            messages.error(
                request,
                f"در بررسی فایل {e} خطا مشاهده شد. هیچ رکوردی ثبت نشد تا خطاها را اصلاح کنید.",
            )

            return redirect("manager:student-import")


        if result["success"]:
            messages.success(
                request,
                f"تعداد {result['created_count']} دانش‌آموز با موفقیت به مدرسه «{school.name}» اضافه شدند.",
            )
            return redirect("manager:student-list")

        messages.error(
            request,
            f"در بررسی فایل {len(result['errors'])} خطا مشاهده شد. هیچ رکوردی ثبت نشد تا خطاها را اصلاح کنید.",
        )
        return self.render_to_response(
            self.get_context_data(form=form, import_result=result)
        )


# ============================================================
# مدیریت معلمان مدرسه + مدیریت مجوزها
# ============================================================
class TeacherListView(ManagerMixin, ListView):
    template_name = "manager/users/teacher_list.html"
    context_object_name = "teachers"
    paginate_by = 25
    permission_field = "can_manage_users"

    def get_queryset(self):
        qs = (
            self.get_school_teachers_queryset()
            .annotate(
                classes_count=Count("classes", distinct=True),
                exams_count=Count("exam", distinct=True),
                questions_count=Count("questions", distinct=True),
            )
            .order_by("-pk")
        )
        q = (self.request.GET.get("q") or "").strip()
        status = (self.request.GET.get("status") or "").strip()
        if q:
            qs = qs.filter(
                Q(user__first_name__icontains=q)
                | Q(user__last_name__icontains=q)
                | Q(user__PhoneNumber=q)
            )
        if status == "active":
            qs = qs.filter(is_active=True)
        elif status == "inactive":
            qs = qs.filter(is_active=False)
        return qs


class TeacherCreateView(ManagerMixin, TemplateView):
    template_name = "manager/users/teacher_form.html"
    permission_field = "can_manage_users"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["is_edit"] = False
        if "form" not in ctx:
            ctx["form"] = ManagerTeacherForm(
                initial={
                    "province": self.get_school().province,
                    "city": self.get_school().city,
                    "is_active": True,
                }
            )
        return ctx

    def post(self, request, *args, **kwargs):
        school = self.get_school()
        form = ManagerTeacherForm(request.POST)
        if not form.is_valid():
            messages.error(request, "لطفاً اطلاعات فرم ثبت معلم را بررسی کنید.")
            return self.render_to_response(self.get_context_data(form=form))

        data = form.cleaned_data
        raw_pass = (data.get("password") or "").strip() or (
            data.get("private_code") or data["phone_number"][-8:]
        )
        with transaction.atomic():
            user = User.objects.create_user(
                PhoneNumber=data["phone_number"],
                password=raw_pass,
                first_name=data["first_name"],
                last_name=data["last_name"],
                email=data.get("email") or "",
                gender=data["gender"],
                type_of_user=User.TypeOfUser.TEACHER,
                private_code=data.get("private_code"),
                biography=data.get("biography") or "",
                is_verified=True,
                is_active=bool(data.get("is_active", True)),
            )
            Teacher.objects.create(
                user=user,
                school=school,
                province=data.get("province") or school.province,
                city=data.get("city") or school.city,
                is_active=bool(data.get("is_active", True)),
            )

        messages.success(request, f"معلم «{user.get_full_name()}» با موفقیت به مدرسه اضافه شد.")
        return redirect("manager:teacher-list")


class TeacherUpdateView(ManagerMixin, TemplateView):
    template_name = "manager/users/teacher_form.html"
    permission_field = "can_manage_users"

    def get_teacher(self):
        return get_object_or_404(
            self.get_school_teachers_queryset(), pk=self.kwargs["pk"]
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        teacher = self.get_teacher()
        ctx["teacher_obj"] = teacher
        ctx["is_edit"] = True
        if "form" not in ctx:
            ctx["form"] = ManagerTeacherForm(
                teacher_instance=teacher,
                initial={
                    "phone_number": str(teacher.user.PhoneNumber),
                    "first_name": teacher.user.first_name,
                    "last_name": teacher.user.last_name,
                    "email": teacher.user.email,
                    "gender": teacher.user.gender,
                    "private_code": teacher.user.private_code,
                    "province": teacher.province,
                    "city": teacher.city,
                    "biography": teacher.user.biography,
                    "is_active": teacher.is_active,
                },
            )
        return ctx

    def post(self, request, *args, **kwargs):
        teacher = self.get_teacher()
        form = ManagerTeacherForm(request.POST, teacher_instance=teacher)
        if not form.is_valid():
            messages.error(request, "لطفاً اطلاعات فرم ویرایش معلم را بررسی کنید.")
            return self.render_to_response(self.get_context_data(form=form))

        data = form.cleaned_data
        user = teacher.user
        with transaction.atomic():
            user.PhoneNumber = data["phone_number"]
            user.first_name = data["first_name"]
            user.last_name = data["last_name"]
            user.email = data.get("email") or ""
            user.gender = data["gender"]
            user.private_code = data.get("private_code")
            user.biography = data.get("biography") or ""
            user.is_active = bool(data.get("is_active", False))
            if data.get("password"):
                user.set_password(data["password"])
            user.save()

            teacher.province = data.get("province")
            teacher.city = data.get("city")
            teacher.is_active = bool(data.get("is_active", False))
            teacher.save()

        messages.success(request, "اطلاعات معلم با موفقیت ویرایش شد.")
        return redirect("manager:teacher-list")


class TeacherPermissionsUpdateView(ManagerMixin, TemplateView):
    """
    ویرایش مجوزهای معلم مدرسه (فقط در صورتی که خود مدیر مجوز can_change_teacher_permissions داشته باشد).
    """

    template_name = "manager/users/teacher_permissions.html"
    permission_field = "can_change_teacher_permissions"

    def get_teacher(self):
        return get_object_or_404(
            self.get_school_teachers_queryset(), pk=self.kwargs["pk"]
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        teacher = self.get_teacher()
        ctx["teacher_obj"] = teacher
        if "form" not in ctx:
            ctx["form"] = TeacherPermissionsForm(instance=teacher)
        return ctx

    def post(self, request, *args, **kwargs):
        teacher = self.get_teacher()
        form = TeacherPermissionsForm(request.POST, instance=teacher)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                f"مجوزهای دسترسی معلم «{teacher}» با موفقیت بروزرسانی شد.",
            )
            return redirect("manager:teacher-list")
        return self.render_to_response(self.get_context_data(form=form))


class TeacherToggleActiveView(ManagerMixin, View):
    permission_field = "can_manage_users"

    def post(self, request, pk, *args, **kwargs):
        teacher = get_object_or_404(self.get_school_teachers_queryset(), pk=pk)
        new_state = self.toggle_object_active(teacher, sync_user=True)
        status_label = "فعال" if new_state else "غیرفعال"
        messages.info(
            request,
            f"وضعیت حساب معلم «{teacher}» به «{status_label}» تغییر یافت (بدون حذف).",
        )
        return redirect(request.META.get("HTTP_REFERER") or "manager:teacher-list")


# ============================================================
# مدیریت مشاوران مدرسه + مدیریت مجوزها
# ============================================================
class AdviserListView(ManagerMixin, ListView):
    template_name = "manager/users/adviser_list.html"
    context_object_name = "advisers"
    paginate_by = 25
    permission_field = "can_manage_users"

    def get_queryset(self):
        qs = (
            self.get_school_advisers_queryset()
            .annotate(
                students_count=Count(
                    "students", filter=Q(students__is_active=True), distinct=True
                ),
                sessions_count=Count("sessions", distinct=True),
                plans_count=Count("created_study_plans", distinct=True),
            )
            .order_by("-pk")
        )
        q = (self.request.GET.get("q") or "").strip()
        status = (self.request.GET.get("status") or "").strip()
        if q:
            qs = qs.filter(
                Q(user__first_name__icontains=q)
                | Q(user__last_name__icontains=q)
                | Q(user__PhoneNumber=q)
                | Q(specialization__icontains=q)
            )
        if status == "active":
            qs = qs.filter(is_active=True)
        elif status == "inactive":
            qs = qs.filter(is_active=False)
        return qs


class AdviserCreateView(ManagerMixin, TemplateView):
    template_name = "manager/users/adviser_form.html"
    permission_field = "can_manage_users"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["is_edit"] = False
        if "form" not in ctx:
            ctx["form"] = ManagerAdviserForm(
                initial={
                    "province": self.get_school().province,
                    "city": self.get_school().city,
                    "max_students_capacity": 50,
                    "is_active": True,
                }
            )
        return ctx

    def post(self, request, *args, **kwargs):
        school = self.get_school()
        form = ManagerAdviserForm(request.POST)
        if not form.is_valid():
            messages.error(request, "لطفاً اطلاعات فرم ثبت مشاور را بررسی کنید.")
            return self.render_to_response(self.get_context_data(form=form))

        data = form.cleaned_data
        raw_pass = (data.get("password") or "").strip() or (
            data.get("private_code") or data["phone_number"][-8:]
        )
        with transaction.atomic():
            user = User.objects.create_user(
                PhoneNumber=data["phone_number"],
                password=raw_pass,
                first_name=data["first_name"],
                last_name=data["last_name"],
                email=data.get("email") or "",
                gender=data["gender"],
                type_of_user=User.TypeOfUser.ADVISER,
                private_code=data.get("private_code"),
                biography=data.get("biography") or "",
                is_verified=True,
                is_active=bool(data.get("is_active", True)),
            )
            Adviser.objects.create(
                user=user,
                school=school,
                specialization=data.get("specialization") or "",
                max_students_capacity=data.get("max_students_capacity") or 50,
                province=data.get("province") or school.province,
                city=data.get("city") or school.city,
                is_active=bool(data.get("is_active", True)),
            )

        messages.success(request, f"مشاور «{user.get_full_name()}» با موفقیت به مدرسه اضافه شد.")
        return redirect("manager:adviser-list")


class AdviserUpdateView(ManagerMixin, TemplateView):
    template_name = "manager/users/adviser_form.html"
    permission_field = "can_manage_users"

    def get_adviser(self):
        return get_object_or_404(
            self.get_school_advisers_queryset(), pk=self.kwargs["pk"]
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        adviser = self.get_adviser()
        ctx["adviser_obj"] = adviser
        ctx["is_edit"] = True
        if "form" not in ctx:
            ctx["form"] = ManagerAdviserForm(
                adviser_instance=adviser,
                initial={
                    "phone_number": str(adviser.user.PhoneNumber),
                    "first_name": adviser.user.first_name,
                    "last_name": adviser.user.last_name,
                    "email": adviser.user.email,
                    "gender": adviser.user.gender,
                    "private_code": adviser.user.private_code,
                    "specialization": adviser.specialization,
                    "max_students_capacity": adviser.max_students_capacity,
                    "province": adviser.province,
                    "city": adviser.city,
                    "biography": adviser.user.biography,
                    "is_active": adviser.is_active,
                },
            )
        return ctx

    def post(self, request, *args, **kwargs):
        adviser = self.get_adviser()
        form = ManagerAdviserForm(request.POST, adviser_instance=adviser)
        if not form.is_valid():
            messages.error(request, "لطفاً اطلاعات فرم ویرایش مشاور را بررسی کنید.")
            return self.render_to_response(self.get_context_data(form=form))

        data = form.cleaned_data
        user = adviser.user
        with transaction.atomic():
            user.PhoneNumber = data["phone_number"]
            user.first_name = data["first_name"]
            user.last_name = data["last_name"]
            user.email = data.get("email") or ""
            user.gender = data["gender"]
            user.private_code = data.get("private_code")
            user.biography = data.get("biography") or ""
            user.is_active = bool(data.get("is_active", False))
            if data.get("password"):
                user.set_password(data["password"])
            user.save()

            adviser.specialization = data.get("specialization") or ""
            adviser.max_students_capacity = data.get("max_students_capacity") or 50
            adviser.province = data.get("province")
            adviser.city = data.get("city")
            adviser.is_active = bool(data.get("is_active", False))
            adviser.save()

        messages.success(request, "اطلاعات مشاور با موفقیت ویرایش شد.")
        return redirect("manager:adviser-list")


class AdviserPermissionsUpdateView(ManagerMixin, TemplateView):
    """
    ویرایش مجوزهای مشاور مدرسه (فقط در صورتی که خود مدیر مجوز can_change_adviser_permissions داشته باشد).
    """

    template_name = "manager/users/adviser_permissions.html"
    permission_field = "can_change_adviser_permissions"

    def get_adviser(self):
        return get_object_or_404(
            self.get_school_advisers_queryset(), pk=self.kwargs["pk"]
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        adviser = self.get_adviser()
        ctx["adviser_obj"] = adviser
        if "form" not in ctx:
            ctx["form"] = AdviserPermissionsForm(instance=adviser)
        return ctx

    def post(self, request, *args, **kwargs):
        adviser = self.get_adviser()
        form = AdviserPermissionsForm(request.POST, instance=adviser)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                f"مجوزها و ظرفیت مشاور «{adviser}» با موفقیت بروزرسانی شد.",
            )
            return redirect("manager:adviser-list")
        return self.render_to_response(self.get_context_data(form=form))


class AdviserToggleActiveView(ManagerMixin, View):
    permission_field = "can_manage_users"

    def post(self, request, pk, *args, **kwargs):
        adviser = get_object_or_404(self.get_school_advisers_queryset(), pk=pk)
        new_state = self.toggle_object_active(adviser, sync_user=True)
        status_label = "فعال" if new_state else "غیرفعال"
        messages.info(
            request,
            f"وضعیت حساب مشاور «{adviser}» به «{status_label}» تغییر یافت (بدون حذف).",
        )
        return redirect(request.META.get("HTTP_REFERER") or "manager:adviser-list")
