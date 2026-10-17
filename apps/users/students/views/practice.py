from django.db.models import Prefetch, Q
from django.views.generic import ListView, View
from apps.users.students.mixins import StudentMixin
from apps.practice.models import Practice, PracticeStudentDetails
from django.shortcuts import get_object_or_404, render, redirect
from apps.questions.models import Question
from django.contrib import messages
from django.db import transaction

from apps.common.utils import datetime2jalali


class StudentPracticeSolveView(StudentMixin, View):
    template_name = "dashboard/practice/question.html"

    def get_objects(self):
        practice = get_object_or_404(
            Practice.objects.filter(is_active=True).select_related("section"),
            pk=self.kwargs["pk"],
        )

        question = get_object_or_404(
            Question.objects.filter(practice=practice, is_active=True).prefetch_related("options"),
            pk=self.kwargs["question_pk"],
        )

        return practice, question

    def get_answer(self, practice, question):
        answer, created = PracticeStudentDetails.objects.get_or_create(
            practice=practice,
            question=question,
            student=self.request.student,
            defaults={
                "status": PracticeStudentDetails.Status.IN_PROGRESS,
                "started_at": datetime2jalali(),
            },
        )

        return answer

    def get(self, request, *args, **kwargs):
        practice, question = self.get_objects()
        answer = self.get_answer(practice, question)

        return render(
            request,
            self.template_name,
            {
                "practice": practice,
                "question": question,
                "answer": answer,
                "options": question.options.all(),
                "is_submitted": answer.status in (
                    PracticeStudentDetails.Status.SUBMITTED,
                    PracticeStudentDetails.Status.CORRECTING,
                    PracticeStudentDetails.Status.CORRECTED,
                ),
            },
        )

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        practice, question = self.get_objects()

        answer = get_object_or_404(
            PracticeStudentDetails.objects.select_for_update(),
            practice=practice,
            question=question,
            student=request.student,
        )

        if answer.status in (
            PracticeStudentDetails.Status.SUBMITTED,
            PracticeStudentDetails.Status.CORRECTING,
            PracticeStudentDetails.Status.CORRECTED,
        ):
            messages.error(request, "این پاسخ قبلاً ارسال شده و امکان ویرایش ندارد.")
            return redirect(request.path)

        if question.type_of_question == Question.TypeOfQuestions.MULTIPLE_CHOICE:
            option_id = request.POST.get("selected_option")

            if option_id:
                answer.selected_option = get_object_or_404(
                    question.options.all(),
                    pk=option_id,
                )
            else:
                answer.selected_option = None

        else:
            answer.answer_text = request.POST.get("answer_text", "").strip()

            answer_image = request.FILES.get("answer_image")
            answer_pdf = request.FILES.get("answer_pdf")

            if answer_image:
                answer.answer_image = answer_image

            if answer_pdf:
                answer.answer_pdf = answer_pdf

        if request.POST.get("action") == "submit":
            answer.status = PracticeStudentDetails.Status.SUBMITTED
            answer.submitted_at = datetime2jalali()
            answer.student_finished_at = datetime2jalali()
            messages.success(request, "پاسخ شما با موفقیت ارسال شد.")
        else:
            answer.status = PracticeStudentDetails.Status.IN_PROGRESS
            messages.success(request, "پاسخ شما ذخیره شد.")

        answer.save()

        return redirect(request.path)

class StudentPracticeDetailView(StudentMixin, View):
    template_name = "dashboard/practice/details.html"

    def get(self, request, *args, **kwargs):
        student = request.student

        practice = get_object_or_404(
            Practice.objects.filter(
                pk=kwargs["pk"],
                is_active=True
            ).filter(
                Q(selected_students=student)
                | Q(selected_students__isnull=True)
            ).prefetch_related(
                Prefetch(
                    "question",

                    to_attr="practice_questions",
                )
            ).distinct()
        )

        questions = practice.practice_questions

        return render(
            request,
            self.template_name,
            {
                "practice": practice,
                "questions": questions,

            },
        )

class StudentPracticeListView(StudentMixin, ListView):
    model = Practice
    template_name = "dashboard/practice/list.html"
    context_object_name = "practices"
    paginate_by = 48

    def get_queryset(self):
        student = self.request.student

        student_details = PracticeStudentDetails.objects.filter(
            student=student
        )

        return (
            Practice.objects
            .filter(
                Q(selected_students__isnull=True)
                | Q(selected_students=student)
            )
            .select_related("section", "creator")
            .prefetch_related(
                Prefetch(
                    "student_details",
                    queryset=student_details,
                    to_attr="current_student_details",
                )
            )
            .distinct()
            .order_by("-sort_number", "-pk")
        )


