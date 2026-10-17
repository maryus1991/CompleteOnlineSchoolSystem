from django.db.models import Prefetch
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView, View
from apps.classes.models import Class
from apps.exams.models import Exam
from apps.questions.models import Question
from apps.users.students.models import Student
from apps.users.teachers.forms.exam import ExamForm
from apps.users.teachers.mixins import TeacherMixin



def _teacher_exams(teacher):
    return Exam.objects.filter(teacher=teacher, is_active=True)

class ExamListView(TeacherMixin, ListView):
    """exam list view for teacher"""

    permission_field = "can_add_exam"
    template_name = "teacher/exam/list.html"
    context_object_name = "items"
    paginate_by = 100

    def get_queryset(self):
        return (
            _teacher_exams(self.request.teacher)
            .select_related("grade", "major", "lesson")
            .order_by("-pk")
        )

class ExamCreateView(TeacherMixin, CreateView):
    """create  exam for teacher"""

    permission_field = "can_add_exam"
    model = Exam
    form_class = ExamForm
    template_name = "teacher/exam/form.html"
    success_url = reverse_lazy("teacher:exam-list")
    message_info = "هر چه قدر عدد موجود در قسمت ترتیب بزرگتر باشد ان مورد بالاتر قرار داده میشود"


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "ساخت آزمون جدید"
        context["page_subtitle"] = "اطلاعات آزمون را وارد کنید"
        context["is_update"] = False
        return context

    def form_valid(self, form):
        self.object = form.save()
        self.object.teacher.add(self.request.teacher)
        messages.success(self.request, "آزمون با موفقیت ثبت شد.")
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        messages.error(self.request, form.errors)
        return self.render_to_response(self.get_context_data(form=form))

class ExamUpdateView(TeacherMixin, UpdateView): # can change status
    """update exam for teacher"""
    permission_field = "can_add_exam"
    message_info = "هر چه قدر عدد موجود در قسمت ترتیب بزرگتر باشد ان مورد بالاتر قرار داده میشود"

    model = Exam
    form_class = ExamForm
    template_name = "teacher/exam/form.html"
    success_url = reverse_lazy("teacher:exam-list")
    context_object_name = "exam"

    def get_queryset(self):
        return _teacher_exams(self.request.teacher)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "ویرایش آزمون"
        context["page_subtitle"] = "اطلاعات آزمون را بروزرسانی کنید"
        context["is_update"] = True
        return context

    def form_valid(self, form):
        messages.success(self.request, "تغییرات آزمون ذخیره شد.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, form.errors)
        return self.render_to_response(self.get_context_data(form=form))

class ExamDeleteView(TeacherMixin, DeleteView):
    """delete exam for teacher"""

    permission_field = "can_add_exam"
    model = Exam
    template_name = "teacher/exam/confirm_delete.html"
    success_url = reverse_lazy("teacher:exam-list")
    context_object_name = "exam"

    def get_queryset(self):
        return _teacher_exams(self.request.teacher)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.is_active = False
        self.object.save(update_fields=["is_active"])
        messages.success(request, "آزمون حذف شد (غیرفعال گردید).")
        return HttpResponseRedirect(self.get_success_url())

    def form_valid(self, form):
        return self.delete(self.request)

class ExamAddAndRemoveStudentView(TeacherMixin, View):
    """Add and remove students from an exam."""

    permission_field = "can_add_exam"
    template_name = "teacher/exam/students.html"

    def get_exam(self):
        return get_object_or_404(
            _teacher_exams(self.request.teacher),
            pk=self.kwargs["pk"],
        )

    def get(self, request, pk):
        exam = self.get_exam()

        selected_ids = set(
            exam.selected_student.values_list("pk", flat=True)
        )

        active_students = (
            Student.objects.filter(is_active=True)
            .select_related("user")
            .order_by("pk")
        )

        classes = (
            Class.objects.filter(
                teacher=request.teacher,
                is_active=True,
            )
            .select_related("grade", "major", "lesson")
            .order_by("-pk")
            .prefetch_related(
                Prefetch(
                    "student",
                    queryset=active_students,
                    to_attr="active_students",
                )
            )
        )

        classes_data = [
            {
                "class": cls,
                "students": [
                    {
                        "student": student,
                        "selected": student.pk in selected_ids,
                    }
                    for student in cls.active_students
                ],
            }
            for cls in classes
        ]

        return render(
            request,
            self.template_name,
            {
                "exam": exam,
                "classes_data": classes_data,
                "selected_count": len(selected_ids),
            },
        )

    def post(self, request, pk):
        exam = self.get_exam()

        action = request.POST.get("action")


        if action in {"add", "remove"}:
            student_ids = [request.POST.get("student_id")]
        elif action in {"add_bulk", "remove_bulk"}:
            student_ids = request.POST.getlist("student_ids")
        else:
            messages.error(request, "عملیات نامعتبر است.")
            return redirect("teacher:exam-students", pk=exam.pk)

        student_ids = list({sid for sid in student_ids if sid})

        if not student_ids:
            messages.error(request, "حداقل یک دانش‌آموز را انتخاب کنید.")
            return redirect("teacher:exam-students", pk=exam.pk)


        students = list(
            Student.objects.filter(
                pk__in=student_ids,
                is_active=True,
                classes__teacher=request.teacher,
                classes__is_active=True,
            )
            .distinct()
        )


        if len(students) != len(student_ids):
            messages.error(
                request,
                "برخی از دانش‌آموزان نامعتبر هستند یا به آن‌ها دسترسی ندارید.",
            )
            return redirect("teacher:exam-students", pk=exam.pk)

        if action in {"add", "add_bulk"}:
            exam.selected_student.add(*students)

            if action == "add":
                messages.success(request, f"{students[0]} به آزمون اضافه شد.")
            else:
                messages.success(
                    request,
                    f"{len(students)} دانش‌آموز به آزمون اضافه شدند.",
                )

        else:
            exam.selected_student.remove(*students)

            if action == "remove":
                messages.success(request, f"{students[0]} از آزمون حذف شد.")
            else:
                messages.success(
                    request,
                    f"{len(students)} دانش‌آموز از آزمون حذف شدند.",
                )

        return redirect("teacher:exam-students", pk=exam.pk)

class ExamAddAndRemoveQuestionsView(TeacherMixin, View):
    """add and remove the exam question for teacher"""
    permission_field = "can_add_exam"
    template_name = "teacher/exam/questions.html"

    def get_exam(self):
        return get_object_or_404(
            _teacher_exams(self.request.teacher),
            pk=self.kwargs["pk"],
        )

    def _base_qs(self, teacher, exam):
        qs = Question.objects.filter(teacher=teacher, is_active=True)
        filters = Q()
        if exam.grade_id:
            filters &= Q(grade_id=exam.grade_id) | Q(grade__isnull=True)
        if exam.major_id:
            filters &= Q(major_id=exam.major_id) | Q(major__isnull=True)
        if exam.lesson_id:
            filters &= Q(lesson_id=exam.lesson_id) | Q(lesson__isnull=True)
        if filters:
            qs = qs.filter(filters)
        return qs.select_related("grade", "major", "lesson").order_by("-sort_number", "-pk")

    def get(self, request, pk):
        from django.shortcuts import render

        exam = self.get_exam()
        qs = self._base_qs(request.teacher, exam)

        assigned = qs.filter(exam=exam)
        available = qs.filter(Q(exam__isnull=True) | ~Q(exam=exam))

        return render(
            request,
            self.template_name,
            {
                "exam": exam,
                "assigned_questions": assigned,
                "available_questions": available,
                "assigned_count": assigned.count(),
            },
        )

    def post(self, request, pk):
        exam = self.get_exam()
        action = request.POST.get("action")
        question_id = request.POST.get("question_id")

        if not question_id:
            messages.error(request, "سوال مشخص نشده است.")
            return redirect("teacher:exam-questions", pk=exam.pk)

        question = (
            Question.objects.filter(
                pk=question_id,
                teacher=request.teacher,
                is_active=True,
            )
            .first()
        )
        if not question:
            messages.error(request, "سوال یافت نشد.")
            return redirect("teacher:exam-questions", pk=exam.pk)

        if action == "add":
            question.exam = exam
            question.save(update_fields=["exam"])
            messages.success(request, f"سوال «{question.name}» به آزمون اضافه شد.")
        elif action == "remove":
            if question.exam_id == exam.pk:
                question.exam = None
                question.save(update_fields=["exam"])
                messages.success(request, f"سوال «{question.name}» از آزمون حذف شد.")

        return redirect("teacher:exam-questions", pk=exam.pk)
