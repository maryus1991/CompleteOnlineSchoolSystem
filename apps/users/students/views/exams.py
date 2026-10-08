
from django.contrib import  messages
from datetime import timedelta
from apps.exams.models import Exam, ExamStudentDetails
from django.views.generic import ListView, View, RedirectView
from apps.users.students.mixins import StudentMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy, reverse
from apps.questions.models import Question, QuestionOption, StudentAnswer
from apps.common.utils import datetime2jalali

from django.http import HttpResponse

class ExamListView(StudentMixin, ListView):
    """exam list view for student dashboard"""

    template_name = 'dashboard/exam/list.html'
    context_object_name = 'items'

    def get_queryset(self):
        return self.request.student.exam.select_related("grade", "major", "lesson")

    def get_context_data(self, *args, **kwargs) :

        data = super().get_context_data(*args, **kwargs)
        data['status'] = Exam.ExamStatus
        return data

class SetExamInformationView(StudentMixin, RedirectView):
    """for set exam information by student"""

    def get_redirect_url(self, *args, **kwargs):
        exam = get_object_or_404(Exam.objects.filter(pk=kwargs['pk'], is_active=True)  , pk=kwargs['pk'])
        request = self.request
        now = datetime2jalali()

        if now < exam.start_at:
            messages.error(request, "آزمون هنوز شروع نشده است.")
            return reverse_lazy("exam:details", kwargs={"pk": exam.pk})

        if now > exam.stop_at:
            messages.error(request, "آزمون پایان یافته است.")
            return reverse_lazy("exam:details", kwargs={"pk": exam.pk})

        if now > exam.last_enter:
            messages.error(request, "مهلت ورود به آزمون تمام شده است.")
            return reverse_lazy("exam:details", kwargs={"pk": exam.pk})

        ExamStudentDetails.objects.get_or_create(exam=exam, student=request.student)

        return reverse_lazy("student:exam-start", kwargs={"pk": exam.pk})

class StartExamView(StudentMixin, View):
    """for start exam"""

    template_name = 'dashboard/exam/start-exam.html'

    def get(self, request, *args, **kwargs):
        exam = get_object_or_404(
            Exam.objects.filter(pk=kwargs['pk'], is_active=True),
            pk=kwargs['pk']
        )

        now = datetime2jalali()

        if now < exam.start_at:
            messages.error(request, "آزمون هنوز شروع نشده است.")
            return redirect("exam:details", pk=exam.pk)

        if now > exam.stop_at:
            messages.error(request, "آزمون پایان یافته است.")
            return redirect("exam:details", pk=exam.pk)

        if now > exam.last_enter:
            messages.error(request, "مهلت ورود به آزمون تمام شده است.")
            return redirect("exam:details", pk=exam.pk)

        start_exam_history = ExamStudentDetails.objects.filter(exam=exam, student=request.student).first()

        if not start_exam_history:
            messages.error(request, "مهلت ورود به آزمون تمام شده است.")
            return redirect("exam:details", pk=exam.pk)

        answered_ids = StudentAnswer.objects.filter(
            exam=exam,
            student=request.student,
        ).exclude(
            type_of_answer=StudentAnswer.TypeOfAnswer.NOT_ANSWERED
        ).values_list('question_id', flat=True)

        base_qs = exam.question.filter(
            is_active=True,
            is_for_qbank=False,
        )

        question = None

        if exam.change_the_order:
            question = base_qs.exclude(pk__in=answered_ids).order_by('?').first()

        elif kwargs.get('pk') and not exam.allow_return_to_questions:
            question = base_qs.get(pk=kwargs['pk'])

        else:
            question = base_qs.exclude(pk__in=answered_ids).order_by("-sort_number", "-id").first()

        if question is None:
            question = base_qs.first()


        remaining_seconds = (
            start_exam_history.created_at
            + timedelta(minutes=exam.time_minutes)
            - now
        ).total_seconds()

        context = {
            'exam': exam,
            'exam_question': question,
            'remaining_seconds': remaining_seconds,
            "start_exam_history": start_exam_history,
            "exam_children_list": exam.children.filter(is_active=True).all(),
            "answered_ids": answered_ids,
            "all_questions": base_qs.values_list("id"),
            "skipped_questions": StudentAnswer.objects.filter(
                exam=exam,
                student=request.student,
                type_of_answer=StudentAnswer.TypeOfAnswer.SKIPPED
            ).values_list('question_id', flat=True),

        }

        return render(request, self.template_name, context)




class ExamSetAnswerOptions(StudentMixin, RedirectView):
    """ثبت یا تغییر پاسخ گزینه‌ای دانش‌آموز"""

    def get_redirect_url(self, *args, **kwargs):
        exam_id = kwargs.get("pk")
        option_id = kwargs.get("option_id")
        question_id = kwargs.get("question_id")

        question = get_object_or_404(Question.objects.select_related("exam"), exam_id=exam_id, pk=question_id )
        option = get_object_or_404(QuestionOption, question=question, pk=option_id)

        answer, created = StudentAnswer.objects.get_or_create(
            exam=question.exam,
            student=self.request.student,
            corrected_at=datetime2jalali(),
            question=question,
            defaults={
                "selected_option": option,
                "type_of_answer": StudentAnswer.TypeOfAnswer.OPTION,
            },
        )

        if not created:
            if not question.exam.allow_to_edit_the_answered_questions:
                messages.error(self.request, "در این آزمون اجازه تغییر پاسخ ثبت‌ شده را ندارید." )
                return reverse("exam:exam-start", kwargs={"pk": question.exam.pk})

            answer.selected_option = option

        if option.is_correct:

            answer.score = question.score
            answer.corrected = StudentAnswer.TypeOfCorrect.excellent
        else:

            answer.score =   -( question.score * question.exam.reduce_percent_of_negative_score / 100 )
            answer.corrected = StudentAnswer.TypeOfCorrect.wrong

        answer.save(update_fields=["selected_option", "score", "type_of_answer", "corrected"])

        messages.success( self.request, "پاسخ با موفقیت ثبت شد." if created else "پاسخ با موفقیت تغییر کرد." )

        return reverse("exam:exam-start", kwargs={"pk": question.exam.pk} )

class ExamSetSkippedToQuestion(StudentMixin, RedirectView):
    """ثبت سؤال به عنوان رد شده"""

    def get_redirect_url(self, *args, **kwargs):
        exam_id = kwargs.get("pk")
        question_id = kwargs.get("question_id")

        question = get_object_or_404(Question.objects.select_related("exam"), exam_id=exam_id, pk=question_id)
        exam  = question.exam
        answer, created = StudentAnswer.objects.get_or_create(
            exam=exam,
            student=self.request.student,
            question=question,
        )

        answer.type_of_answer = StudentAnswer.TypeOfAnswer.SKIPPED
        answer.selected_option = None
        answer.score = 0

        answer.save(
            update_fields=[
                "type_of_answer",
                "is_skipped",
                "selected_option",
                "score",
            ]
        )

        messages.warning(self.request, "سؤال به حالت رد شده تبدیل شد.")
        return reverse("exam:exam-start", kwargs={"pk": exam.pk} )

class ExamFinished(StudentMixin, RedirectView):
        """quiz finished"""

        def get_redirect_url(self, *args, **kwargs):
            pk = kwargs['pk']
            student = self.request.student

            exam = get_object_or_404(Exam.objects.select_related('exam'), pk=pk, student=student)

            ExamStudentDetails.objects.filter(
                exam=exam,
                student=student,
            ).update(
                student_finished_at=datetime2jalali(),
            )
            messages.success(
                self.request,
                'از آزمون با موفقیت به پایان رساندید, خسته نباشید'
            )
            return reverse(
                'exam:details',
                kwargs={'pk': exam.pk}
            )

