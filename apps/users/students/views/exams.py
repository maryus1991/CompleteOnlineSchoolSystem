#
# from django.utils import timezone
# from django_jalali.utils import datetime2jalali
# from django.contrib import  messages
# from apps.exams.models import Exam, ExamStudentDetails
# from django.views.generic import ListView, View, RedirectView
# from apps.users.students.mixins import StudentMixin
# from django.shortcuts import get_object_or_404, redirect, render
# from django.urls import reverse_lazy
# from apps.questions.models import Question, QuestionOption, StudentAnswer
#
#
# class ExamListView(StudentMixin, ListView):
#     """exam list view for student dashboard"""
#
#     template_name = 'dashboard/exam/list.html'
#     context_object_name = 'items'
#
#     def get_queryset(self):
#         return self.request.student.exam.select_related("grade", "major", "lesson")
#
#     def get_context_data(self, *args, **kwargs) :
#
#         data = super().get_context_data(*args, **kwargs)
#         data['status'] = Exam.ExamStatus
#         return data
#
# class SetExamInformationView(StudentMixin, RedirectView):
#     """for set exam information by student"""
#
#     def get_redirect_url(self, request, *args, **kwargs):
#         exam = get_object_or_404(Exam.objects.filter(pk=kwargs['pk']) , is_active=True , pk=kwargs['pk'])
#
#         now = datetime2jalali(timezone.now())
#
#         if now < exam.start_at:
#             messages.error(request, "آزمون هنوز شروع نشده است.")
#             return reverse_lazy("exam:details", kwargs={"pk": exam.pk})
#
#         if now > exam.stop_at:
#             messages.error(request, "آزمون پایان یافته است.")
#             return reverse_lazy("exam:details", kwargs={"pk": exam.pk})
#
#         if now > exam.last_enter:
#             messages.error(request, "مهلت ورود به آزمون تمام شده است.")
#             return reverse_lazy("exam:details", kwargs={"pk": exam.pk})
#
#         ExamStudentDetails.objects.get_or_create(exam=exam, studetn=request.student)
#
#         return reverse_lazy("exam:details", kwargs={"pk": exam.pk})
#
# class StartExamView(StudentMixin, View):
#     """for start exam"""
#
#     template_name = 'dashboard/exam/start-exam.html'
#
#     def get(self, request, *args, **kwargs):
#         exam = get_object_or_404(Exam.objects.filter(pk=kwargs['pk']).prefetch_related("question", "children") , is_active=True , pk=kwargs['pk'])
#
#         now = datetime2jalali(timezone.now())
#
#         if now < exam.start_at:
#             messages.error(request, "آزمون هنوز شروع نشده است.")
#             return redirect("exam:details", pk= exam.pk)
#
#         if now > exam.stop_at:
#             messages.error(request, "آزمون پایان یافته است.")
#             return redirect("exam:details", pk= exam.pk)
#
#         if now > exam.last_enter:
#             messages.error(request, "مهلت ورود به آزمون تمام شده است.")
#             return redirect("exam:details", pk= exam.pk)
#
#         if not ExamStudentDetails.objects.filter(exam=exam, studetn=request.student).exists():
#             messages.error(request, "مهلت ورود به آزمون تمام شده است.")
#             return redirect("exam:details", pk= exam.pk)
#
#         # todo: fix the order of question
#
#         context = {
#             'exam': exam,
#             'children': exam.children.filter(is_active=True).all(),
#             'question': exam.question.filter(is_active=True, is_for_qbank=False).first(),
#         }
#
#         return render(request, self.template_name, context)
#
# class ExamSetAnswerOptions(StudentMixin, RedirectView):
#     """ثبت یا تغییر پاسخ گزینه‌ای دانش‌آموز"""
#
#     def get_redirect_url(self, *args, **kwargs):
#         exam_id = kwargs.get("pk")
#         option_id = kwargs.get("option_id")
#         question_id = kwargs.get("question_id")
#
#         question = get_object_or_404(Question.objects.select_related("exam"), exam_id=exam_id, pk=question_id )
#         option = get_object_or_404(QuestionOption, question=question, pk=option_id)
#
#         answer, created = StudentAnswer.objects.get_or_create(
#             exam=question.exam,
#             student=self.request.student,
#             corrected_at=datetime2jalali(timezone.now()),
#             question=question,
#             defaults={
#                 "selected_option": option,
#                 "type_of_answer": StudentAnswer.TypeOfAnswer.OPTION,
#             },
#         )
#
#         if not created:
#             if not question.exam.allow_to_edit_the_answered_questions:
#                 messages.error(self.request, "در این آزمون اجازه تغییر پاسخ ثبت‌ شده را ندارید." )
#                 return reverse("exam:exam-start", kwargs={"pk": question.exam.pk})
#
#             answer.selected_option = option
#
#         if option.is_correct:
#
#             answer.score = question.score
#             answer.corrected = StudentAnswer.TypeOfCorrect.excellent
#         else:
#
#             answer.score =   -( question.score * question.exam.reduce_percent_of_negative_score / 100 )
#             answer.corrected = StudentAnswer.TypeOfCorrect.wrong
#
#         answer.save(update_fields=["selected_option", "score", "type_of_answer", "corrected"])
#
#         messages.success( self.request, "پاسخ با موفقیت ثبت شد." if created else "پاسخ با موفقیت تغییر کرد." )
#
#         return reverse("exam:exam-start", kwargs={"pk": question.exam.pk} )
#
# class ExamSetSkippedToQuestion(StudentMixin, RedirectView):
#     """ثبت سؤال به عنوان رد شده"""
#
#     def get_redirect_url(self, *args, **kwargs):
#         exam_id = kwargs.get("pk")
#         question_id = kwargs.get("question_id")
#         exam = get_object_or_404(Exam, pk=exam_id, student=self.request.student)
#         question = get_object_or_404(Question, exam=exam, pk=question_id)
#         answer, created = StudentAnswer.objects.get_or_create(
#             exam=exam,
#             student=self.request.student,
#             question=question,
#         )
#
#         answer.type_of_answer = StudentAnswer.TypeOfAnswer.SKIPPED
#         answer.selected_option = None
#         answer.score = 0
#
#         answer.save(
#             update_fields=[
#                 "type_of_answer",
#                 "is_skipped",
#                 "selected_option",
#                 "score",
#             ]
#         )
#
#         messages.warning(self.request, "سؤال به حالت رد شده تبدیل شد.")
#         return reverse("exam:exam-start", kwargs={"pk": quiz.pk} )
#
# class ExamFinished(StudentMixin, RedirectView):
#         """quiz finished"""
#
#         def get_redirect_url(self, *args, **kwargs):
#             pk = kwargs['pk']
#             student = self.request.student
#
#             exam = get_object_or_404(Exam.objects.select_related('exam'), pk=pk, student=student)
#
#             ExamStudentDetails.objects.filter(
#                 exam=exam,
#                 student=student,
#             ).update(
#                 student_finished_at=datetime2jalali(timezone.now()),
#             )
#             messages.success(
#                 self.request,
#                 'از آزمون با موفقیت به پایان رساندید, خسته نباشید'
#             )
#             return reverse(
#                 'exam:details',
#                 kwargs={'pk': exam.pk}
#             )
#
#
# class ExamSetAnswerTextOrFiles(LoginRequiredMixin, RedirectView):
#     """for upload files"""
#
#     def get_redirect_url(self, *args, **kwargs):
#         item = get_object_or_404(
#             StudentAnswer,
#             question_id=kwargs.get('question_id'),
#             exam_id=kwargs.get('pk'),
#             student=self.request.student
#         )
#
#         form = AnswerForm(self.request.POST, self.request.FILES)
#
#         if not item.quiz.allow_to_edit_the_answered_questions:
#             messages.error(self.request, 'در این ازمون اجازه تغییر پاسخ ثبت شده')
#             return reverse('quiz:quiz-start', kwargs={'pk': kwargs.get('pk')})
#
#         if form.is_valid():
#
#             if text := form.cleaned_data.get('answer'):
#                 item.description = text
#                 item.type_of_answer = StudentAnswer.TypeOfAnswer.TEXT_BASED
#
#             if file := form.cleaned_data.get('file'):
#
#                 if file.content_type in ['application/pdf']:
#
#                     item.pdf_file = form.files.get('file')
#                     item.type_of_answer = StudentAnswer.TypeOfAnswer.PDF_BASED
#
#
#                 else:
#                     item.image = form.files.get('file')
#                     item.type_of_answer = StudentAnswer.TypeOfAnswer.IMAGE_BASED
#
#             if image := form.cleaned_data.get('image'):
#                 item.image = form.files.get('image')
#                 item.type_of_answer = StudentAnswer.TypeOfAnswer.IMAGE_BASED
#
#             item.created_at = now()
#             item.save()
#             messages.success(self.request, 'پاسخ ثبت شد')
#         else:
#             messages.error(self.request, form.errors)
#
#         return reverse('quiz:quiz-start', kwargs={'pk': kwargs.get('pk')})
#
#
# class QuizAnswerRemoveImage(LoginRequiredMixin, RedirectView):
#     """for delete the image"""
#
#     def get_redirect_url(self, *args, **kwargs):
#         item = get_object_or_404(
#             StudentAnswer,
#             question_id=kwargs.get('question_id'),
#             quiz_id=kwargs.get('pk'),
#             student=self.request.user
#         )
#
#         item.image = None
#         item.save()
#         messages.success(self.request, 'عکس حذف شد')
#
#         return reverse('quiz:quiz-start', kwargs={'pk': kwargs.get('pk')})
#
#
# class QuizAnswerRemovePDF(LoginRequiredMixin, RedirectView):
#     """for delete the image"""
#
#     def get_redirect_url(self, *args, **kwargs):
#         item = get_object_or_404(
#             StudentAnswer,
#             question_id=kwargs.get('question_id'),
#             quiz_id=kwargs.get('pk'),
#             student=self.request.user
#         )
#
#         item.pdf_file = None
#         item.save()
#         messages.success(self.request, 'pdf حذف شد')
#
#         return reverse('quiz:quiz-start', kwargs={'pk': kwargs.get('pk')})
#
#
