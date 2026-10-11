from django.db.models import Prefetch, Q
from django.views.generic import ListView, View
from apps.users.students.mixins import StudentMixin
from apps.practice.models import Practice, PracticeStudentDetails
from django.shortcuts import get_object_or_404, render
from apps.questions.models import Question, QuestionOption


class StudentPracticeDetailView(StudentMixin, View):
    template_name = "dashboard/practice/details.html"

    def get(self, request, *args, **kwargs):
        student = request.student

        practice = get_object_or_404(
            Practice.objects.filter(
                pk=kwargs["pk"],
            ).filter(
                Q(selected_students=student)
                | Q(selected_students__isnull=True)
            ).prefetch_related(
                Prefetch(
                    "question",
                    queryset=Question.objects.filter(
                        is_for_qbank=False
                    ).prefetch_related(
                        Prefetch(
                            "options",
                            queryset=QuestionOption.objects.order_by(
                                "-sort_number", "-pk"
                            ),
                        )
                    ).order_by("-sort_number", "-pk"),
                    to_attr="practice_questions",
                )
            ).distinct()
        )

        questions = practice.practice_questions

        answers = {
            answer.question_id: answer
            for answer in PracticeStudentDetails.objects.filter(
                practice=practice,
                student=student,
                question__in=questions,
            )
        }

        return render(
            request,
            self.template_name,
            {
                "practice": practice,
                "questions": questions,
                "answers": answers,
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


