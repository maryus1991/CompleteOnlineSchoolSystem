
from django.contrib import  messages
from datetime import timedelta
from apps.exams.models import Exam, ExamStudentDetails
from django.views.generic import ListView, View, RedirectView
from apps.users.students.mixins import StudentMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy, reverse
from apps.questions.models import Question, QuestionOption, StudentAnswer
from apps.common.utils import datetime2jalali
from django.db.models import Exists, OuterRef

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
            Exam.objects.filter(pk=kwargs['pk'], is_active=True).select_related("grade", "major", "lesson"),
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
            return redirect("student:exam-information", pk=exam.pk)

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

        remaining_time = (
                start_exam_history.created_at
                + timedelta(minutes=exam.time_minutes)
                - now
        )


        skipped_questions = StudentAnswer.objects.filter(
            exam=exam,
            student=request.student,
            type_of_answer=StudentAnswer.TypeOfAnswer.SKIPPED
        ).values_list('question_id', flat=True)

        all_questions = base_qs.values_list("id", flat=True)
        exam_children_list = exam.children.filter(is_active=True)
        context = {
            'exam': exam,
            'question': question,
            'remaining_minutes': max(0, remaining_time.total_seconds() / 60 ),
            "started_exams_history_ids": ExamStudentDetails.objects.filter(exam__id__in=exam_children_list.values_list("id", flat=True), student=request.student).values_list("exam__id", flat=True),
            "exam_children_list": exam_children_list.all(),
            "answered_ids": answered_ids,
            "all_questions": all_questions,
            "skipped_questions": skipped_questions,

        }

        context.update({
            "answered_ids_count": len(answered_ids),
            "all_questions_count": len(all_questions),
            "skipped_questions_count": len(skipped_questions),
        })

        try:
            progress_percent = (int(context.get("answered_ids_count")) + int(context.get("skipped_questions_count"))) * 100 / int(context.get("answered_ids_count"))
        except Exception :
            progress_percent = 0


        context.update({
            "progress_percent": progress_percent,
            "answered_ids_count_plus_skipped_questions_count": int(context.get("answered_ids_count")) + int(context.get("skipped_questions_count")) ,
        })

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
    """Finish exam and redirect to the next exam."""

    def get_redirect_url(self, *args, **kwargs):
        student = self.request.student

        exam = get_object_or_404(
            Exam.objects.select_related('parent'),
            pk=kwargs['pk'],
        )

        ExamStudentDetails.objects.filter(
            exam_id=exam.pk,
            student=student,
        ).update(
            student_finished_at=datetime2jalali(),
        )

        if exam.parent:
            completed_exam = ExamStudentDetails.objects.filter(
                exam_id=OuterRef('pk'),
                student=student,
            )

            next_exam = exam.parent.children.filter(
                is_active=True,
            ).annotate(
                has_detail=Exists(completed_exam),
            ).filter(
                has_detail=False,
            ).order_by(
                '-sort_number', '-pk',
            ).first()



            if next_exam:
                return reverse(
                    'student:exam-information',
                    kwargs={'pk': next_exam.pk},
                )
            else:
                messages.info(
                    self.request,
                    "ازمون ها را به موفقیت به پایان رساندید, خسته نباشید"
                )
        else:
            messages.info(
                self.request,
                'آزمون را با موفقیت به پایان رساندید، خسته نباشید.',
            )

        return reverse(
            'exam:details',
            kwargs={'pk': exam.pk},
        )

