from collections import OrderedDict, defaultdict

from django.contrib import messages
from django.db.models import Count, Q, Prefetch
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from apps.classes.models import Class
from apps.content.models import Section
from apps.practice.models import Practice, PracticeStudentDetails
from apps.questions.models import Question
from apps.users.students.models import Student
from apps.users.teachers.forms.practice import PracticeForm, PracticeGradeForm
from apps.users.teachers.mixins import TeacherMixin


def _teacher_classes_qs(teacher):
    return Class.objects.filter(teacher=teacher, is_active=True)


def _teacher_sections_qs(teacher):
    return Section.objects.filter(
        is_active=True,
        klass__teacher=teacher,
        klass__is_active=True,
    )


def _teacher_practices_qs(teacher):
    return Practice.objects.filter(
        is_active=True,
        section__klass__teacher=teacher,
        section__klass__is_active=True,
        section__is_active=True,
    )


class PracticeListView(TeacherMixin, ListView):
    """practice list view"""

    permission_field = "can_add_practice"
    template_name = "teacher/practice/list.html"
    context_object_name = "groups"

    def get_queryset(self): return Practice.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        teacher = self.request.teacher

        practices_qs = (
            Practice.objects.filter(
                is_active=True,
                section__klass__teacher=teacher,
                section__is_active=True,
                section__klass__is_active=True,
            )
            .annotate(
                submitted_count=Count(
                    "student_details",
                    filter=Q(
                        student_details__status__in=[
                            PracticeStudentDetails.Status.SUBMITTED,
                            PracticeStudentDetails.Status.CORRECTING,
                            PracticeStudentDetails.Status.CORRECTED,
                        ]
                    ),
                    distinct=True,
                ),
                corrected_count=Count(
                    "student_details",
                    filter=Q(student_details__status=PracticeStudentDetails.Status.CORRECTED),
                    distinct=True,
                ),
                total_details=Count("student_details", distinct=True),
            )
            .order_by("-sort_number", "-pk")
        )

        sections_qs = (
            _teacher_sections_qs(teacher)
            .select_related("klass", "klass__grade", "klass__lesson")
            .prefetch_related(
                Prefetch("practices", queryset=practices_qs, to_attr="practice_list")
            )
            .order_by("klass__name", "sort_number", "pk")
        )

        grouped = OrderedDict()
        for section in sections_qs:
            klass = section.klass
            if klass.pk not in grouped:
                grouped[klass.pk] = {
                    "klass": klass,
                    "sections": [],
                    "practice_total": 0,
                }
            practices = getattr(section, "practice_list", [])
            grouped[klass.pk]["sections"].append(
                {"section": section, "practices": practices}
            )
            grouped[klass.pk]["practice_total"] += len(practices)

        context["groups"] = list(grouped.values())
        context["total_practices"] = sum(g["practice_total"] for g in context["groups"])
        return context


class PracticeCreateView(TeacherMixin, CreateView):
    """create practice for teacher panel"""

    permission_field = "can_add_practice"
    model = Practice
    form_class = PracticeForm
    template_name = "teacher/practice/form.html"
    success_url = reverse_lazy("teacher:practice-list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["teacher"] = self.request.teacher
        section_id = self.request.GET.get("section") or self.kwargs.get("section_id")
        if section_id:
            section = (
                _teacher_sections_qs(self.request.teacher)
                .filter(pk=section_id)
                .first()
            )
            if section:
                kwargs["section"] = section
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "تعریف تمرین جدید"
        context["page_subtitle"] = "تمرین را به یک جلسه از کلاس‌های خود وصل کنید"
        context["is_update"] = False
        return context

    def form_valid(self, form):
        section = form.cleaned_data["section"]

        if section.klass.teacher_id != self.request.teacher.pk:
            messages.error(self.request, "دسترسی به این جلسه مجاز نیست.")
            return self.form_invalid(form)

        practice = form.save(commit=False)
        practice.creator = self.request.user
        practice.save()


        student_ids = list(
            section.klass.student.filter(is_active=True).values_list("pk", flat=True)
        )
        if student_ids:
            practice.selected_students.set(student_ids)

        messages.success(
            self.request,
            "تمرین ثبت شد. حالا سوال‌های تمرین را انتخاب کنید.",
        )
        return HttpResponseRedirect(
            reverse("teacher:practice-questions", kwargs={"pk": practice.pk})
        )

    def form_invalid(self, form):
        messages.error(self.request, form.errors)
        return self.render_to_response(self.get_context_data(form=form))


class PracticeUpdateView(TeacherMixin, UpdateView):
    """practice update view"""
    permission_field = "can_add_practice"
    model = Practice
    form_class = PracticeForm
    template_name = "teacher/practice/form.html"
    context_object_name = "practice"

    def get_queryset(self):
        return _teacher_practices_qs(self.request.teacher)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["teacher"] = self.request.teacher
        return kwargs

    def get_success_url(self):
        return reverse("teacher:practice-detail", kwargs={"pk": self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "ویرایش تمرین"
        context["page_subtitle"] = self.object.name
        context["is_update"] = True
        return context

    def form_valid(self, form):
        messages.success(self.request, "تغییرات تمرین ذخیره شد.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, form.errors)
        return self.render_to_response(self.get_context_data(form=form))


class PracticeDeleteView(TeacherMixin, DeleteView):
    """practice soft delete """

    permission_field = "can_add_practice"
    model = Practice
    template_name = "teacher/practice/confirm_delete.html"
    success_url = reverse_lazy("teacher:practice-list")
    context_object_name = "practice"

    def get_queryset(self):
        return _teacher_practices_qs(self.request.teacher)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.is_active = False
        self.object.save(update_fields=["is_active"])
        messages.success(request, "تمرین حذف شد (غیرفعال گردید).")
        return HttpResponseRedirect(self.get_success_url())

    def form_valid(self, form):
        return self.delete(self.request)


class PracticeDetailView(TeacherMixin, DetailView):
    """
    practice details view
    """

    permission_field = "can_add_practice"
    model = Practice
    template_name = "teacher/practice/details.html"
    context_object_name = "practice"

    def get_queryset(self):
        return (
            _teacher_practices_qs(self.request.teacher)
            .select_related(
                "section",
                "section__klass",
                "section__klass__grade",
                "section__klass__lesson",
            )
            .prefetch_related(
                Prefetch(
                    "selected_students",
                    queryset=Student.objects.filter(is_active=True)
                    .select_related("user")
                    .only(
                        "id",
                        "user__id",
                        "user__first_name",
                        "user__last_name",
                        "user__PhoneNumber",
                    ),
                ),
                Prefetch(
                    "student_details",
                    queryset=PracticeStudentDetails.objects.select_related(
                        "student",
                        "student__user",
                        "question",
                    ).order_by("student_id", "-pk"),
                ),
            )
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        practice = self.object

        details_by_student = defaultdict(list)
        for d in practice.student_details.all():
            details_by_student[d.student_id].append(d)

        submitted_statuses = {
            PracticeStudentDetails.Status.SUBMITTED,
            PracticeStudentDetails.Status.CORRECTING,
            PracticeStudentDetails.Status.CORRECTED,
            PracticeStudentDetails.Status.IN_PROGRESS,
        }

        answered = []
        not_answered = []

        students = list(practice.selected_students.all())
        if not students and practice.section_id:
            students = list(
                practice.section.klass.student.filter(is_active=True).select_related("user")
            )

        for student in students:
            details = details_by_student.get(student.pk, [])
            has_submit = any(d.status in submitted_statuses for d in details)
            latest = details[0] if details else None
            row = {
                "student": student,
                "details": details,
                "latest": latest,
                "has_submit": has_submit,
            }
            if has_submit:
                answered.append(row)
            else:
                not_answered.append(row)

        context["answered_rows"] = answered
        context["not_answered_rows"] = not_answered
        context["answered_count"] = len(answered)
        context["not_answered_count"] = len(not_answered)
        context["total_students"] = len(answered) + len(not_answered)
        context["questions_count"] = (
            Question.objects.filter(
                practice=practice,
                teacher=self.request.teacher,
                is_active=True,
            ).count()
        )
        return context


class PracticeQuestionsView(TeacherMixin, View):
    """
        set question for practice
    """

    permission_field = "can_add_practice"
    template_name = "teacher/practice/questions.html"

    def get_practice(self):
        return get_object_or_404(
            _teacher_practices_qs(self.request.teacher).select_related(
                "section",
                "section__klass",
                "section__klass__grade",
                "section__klass__major",
                "section__klass__lesson",
            ),
            pk=self.kwargs["pk"],
        )

    def _teacher_questions_qs(self, teacher, practice):
        qs = Question.objects.filter(
            teacher=teacher,
            is_active=True,
        ).filter(Q(practice__isnull=True) | Q(practice=practice)).select_related(
            "grade",
            "major",
            "lesson",
        )

        klass = getattr(practice.section, "klass", None) if practice.section else None

        if klass:
            filters = Q()

            if klass.grade_id:
                filters &= (
                        Q(grade_id=klass.grade_id)
                        | Q(grade__isnull=True)
                )

            if klass.major_id:
                filters &= (
                        Q(major_id=klass.major_id)
                        | Q(major__isnull=True)
                )

            if klass.lesson_id:
                filters &= (
                        Q(lesson_id=klass.lesson_id)
                        | Q(lesson__isnull=True)
                )

            qs = qs.filter(filters)

        return qs.order_by("-sort_number", "-pk")

    def get(self, request, pk):
        practice = self.get_practice()
        qs = self._teacher_questions_qs(request.teacher, practice)


        assigned = list(qs.filter(practice=practice))
        available = list(qs.filter(Q(practice__isnull=True) | ~Q(practice=practice)))

        return render(
            request,
            self.template_name,
            {
                "practice": practice,
                "assigned_questions": assigned,
                "available_questions": available,
                "assigned_count": len(assigned),
            },
        )

    def post(self, request, pk):
        practice = self.get_practice()
        action = request.POST.get("action")
        question_id = request.POST.get("question_id")

        if not question_id:
            messages.error(request, "سوال مشخص نشده است.")
            return redirect("teacher:practice-questions", pk=practice.pk)

        question = (
            Question.objects.filter(
                pk=question_id,
                teacher=request.teacher,
                is_active=True,
            )
            .only("id", "name", "practice_id")
            .first()
        )
        if not question:
            messages.error(request, "سوال یافت نشد یا متعلق به شما نیست.")
            return redirect("teacher:practice-questions", pk=practice.pk)

        if action == "add":
            question.practice = practice
            question.save(update_fields=["practice"])
            messages.success(request, f"سوال «{question.name}» به تمرین اضافه شد.")
        elif action == "remove":
            if question.practice_id == practice.pk:
                question.practice = None
                question.save(update_fields=["practice"])
                messages.success(request, f"سوال «{question.name}» از تمرین حذف شد.")

        return redirect("teacher:practice-questions", pk=practice.pk)


class PracticeGradeView(TeacherMixin, View):
    """set score for student answer of practice"""

    permission_field = "can_add_practice"
    template_name = "teacher/practice/grade.html"

    def _get_detail(self, request, pk):
        return get_object_or_404(
            PracticeStudentDetails.objects.select_related(
                "practice",
                "practice__section",
                "practice__section__klass",
                "student",
                "student__user",
                "question",
                "selected_option",
            ),
            pk=pk,
            practice__is_active=True,
            practice__section__klass__teacher=request.teacher,
        )

    def get(self, request, pk):
        detail = self._get_detail(request, pk)
        form = PracticeGradeForm(instance=detail)
        return render(
            request,
            self.template_name,
            {"detail": detail, "form": form, "practice": detail.practice},
        )

    def post(self, request, pk):
        detail = self._get_detail(request, pk)
        form = PracticeGradeForm(request.POST, instance=detail)
        if form.is_valid():
            obj = form.save(commit=False)
            if obj.status == PracticeStudentDetails.Status.CORRECTED:
                obj.corrected_at = timezone.now()
            obj.save()
            messages.success(request, "نمره و بازخورد ذخیره شد.")
            return redirect("teacher:practice-detail", pk=detail.practice_id)

        messages.error(request, form.errors)
        return render(
            request,
            self.template_name,
            {"detail": detail, "form": form, "practice": detail.practice},
        )
