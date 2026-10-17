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
import random
from django.db.models import Subquery


class ExamListView(StudentMixin, ListView):
    """exam list view for student dashboard"""

    template_name = 'dashboard/exam/list.html'
    context_object_name = 'items'

    def get_queryset(self):
        return self.request.student.exam.filter(is_active=True).select_related("grade", "major", "lesson")

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
        student = request.student

        exam = get_object_or_404(
            Exam.objects.select_related("grade", "major", "lesson"),
            pk=kwargs["pk"],
            is_active=True,
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

        start_exam_history = (
            ExamStudentDetails.objects
            .filter(exam=exam, student=student)
            .only("created_at")
            .first()
        )

        if start_exam_history is None:
            messages.error(request, "مهلت ورود به آزمون تمام شده است.")
            return redirect("student:exam-information", pk=exam.pk)

        base_qs = exam.question.filter(
            is_active=True,
            is_for_qbank=False,
        )

        # فقط شناسه‌ها را از دیتابیس دریافت می‌کنیم.
        all_questions = list(
            base_qs.order_by("-sort_number", "-pk")
            .values_list("pk", flat=True)
        )
        all_question_ids = set(all_questions)

        # همه پاسخ‌های دانش‌آموز را فقط یک‌بار می‌خوانیم.
        answer_rows = StudentAnswer.objects.filter(
            exam=exam,
            student=student,
        )

        answered_ids = set()
        skipped_questions = set()
        student_answers = {}

        NOT_ANSWERED = StudentAnswer.TypeOfAnswer.NOT_ANSWERED
        SKIPPED = StudentAnswer.TypeOfAnswer.SKIPPED

        for answer in answer_rows:
            qid = answer.question_id

            if qid not in all_question_ids:
                continue

            # معادل first() در Query قبلی، در صورت وجود چند پاسخ.
            student_answers.setdefault(qid, answer)

            if answer.type_of_answer == SKIPPED:
                skipped_questions.add(qid)
            elif answer.type_of_answer != NOT_ANSWERED:
                answered_ids.add(qid)

        # انتخاب سؤال؛ انتخاب تصادفی در حافظه انجام می‌شود.
        requested_question_id = kwargs.get("question_id")
        question_id = None

        if (
                requested_question_id
                and exam.allow_return_to_questions
                and requested_question_id in all_question_ids
        ):
            question_id = requested_question_id
        else:
            available_ids = [
                qid for qid in all_questions
                if qid not in answered_ids
            ]

            if available_ids:
                question_id = (
                    random.choice(available_ids)
                    if exam.change_the_order
                    else available_ids[0]
                )
            elif all_questions:
                question_id = all_questions[0]

        question = None

        if question_id is not None:
            question = (
                base_qs.filter(pk=question_id)
                .prefetch_related("options")
                .first()
            )

        student_answer = (
            student_answers.get(question.pk)
            if question is not None
            else None
        )

        remaining_time = (
                start_exam_history.created_at
                + timedelta(minutes=exam.time_minutes)
                - now
        )

        exam_children_list = exam.children.filter(is_active=True)

        started_exams_history_ids = (
            ExamStudentDetails.objects
            .filter(
                exam_id__in=Subquery(
                    exam_children_list.values("pk")
                ),
                student=student,
            )
            .values_list("exam_id", flat=True)
        )

        answered_ids_count = len(answered_ids)
        skipped_questions_count = len(skipped_questions)
        all_questions_count = len(all_questions)

        answered_and_skipped_count = (
                answered_ids_count + skipped_questions_count
        )

        progress_percent = (
            answered_and_skipped_count * 100 / all_questions_count
            if all_questions_count
            else 0
        )

        context = {
            "exam": exam,
            "question": question,
            "student_answer": student_answer,
            "remaining_minutes": max(
                0,
                remaining_time.total_seconds() / 60,
            ),
            "start_exam_history": start_exam_history,
            "started_exams_history_ids": started_exams_history_ids,
            "exam_children_list": exam_children_list,
            "answered_ids": answered_ids,
            "all_questions": all_questions,
            "skipped_questions": skipped_questions,
            "answered_ids_count": answered_ids_count,
            "all_questions_count": all_questions_count,
            "skipped_questions_count": skipped_questions_count,
            "progress_percent": progress_percent,
            "answered_ids_count_plus_skipped_questions_count": (
                answered_and_skipped_count
            ),
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
            question=question,
            defaults={
                "selected_option": option,
            }
        )


        if not question.exam.allow_to_edit_the_answered_questions:
            messages.error(self.request, "در این آزمون اجازه تغییر پاسخ ثبت‌ شده را ندارید." )
            return reverse("exam:exam-start", kwargs={"pk": question.exam.pk})
        else:
            answer.selected_option = option

        if option.is_correct:

            answer.score = question.score
            answer.corrected = StudentAnswer.TypeOfCorrect.excellent
        else:

            answer.score =   -( question.score * question.exam.reduce_percent_of_negative_score / 100 )
            answer.corrected = StudentAnswer.TypeOfCorrect.wrong

        answer.type_of_answer = StudentAnswer.TypeOfAnswer.OPTION
        answer.corrected_at=datetime2jalali()
        answer.save(update_fields=["selected_option", "score", "type_of_answer", "corrected_at", "corrected"])

        messages.success( self.request, "پاسخ با موفقیت ثبت شد." if created else "پاسخ با موفقیت تغییر کرد." )

        return reverse("student:exam-start", kwargs={"pk": question.exam.pk} )

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
        answer.corrected = StudentAnswer.TypeOfCorrect.wrong
        answer.corrected_at =  datetime2jalali()
        answer.selected_option = None
        answer.score = 0

        answer.save(
            update_fields=[
                "type_of_answer",
                "selected_option",
                "corrected",
                "corrected_at",
                "score",
            ]
        )

        messages.warning(self.request, "سؤال به حالت رد شده تبدیل شد.")
        return reverse("student:exam-start", kwargs={"pk": exam.pk} )


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


# todo: add pdf and image for student answer upload and delete
