from django.contrib import messages
from django.db.models import Avg, Count, Max, Min, Q
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.views.generic import ListView, TemplateView

from apps.categories.models import GradeCategories, LessonCategories, MajorCategories
from apps.exams.models import Exam
from apps.practice.models import Practice, PracticeStudentDetails
from apps.questions.models import Question, StudentAnswer
from apps.reports.models import ExamReport
from apps.users.managers.forms.exams import (
    ManagerExamForm,
    ManagerExamStatusForm,
    ManagerPracticeForm,
)
from apps.users.managers.mixins import ManagerMixin


class ExamListView(ManagerMixin, ListView):
    template_name = "manager/exams/exam_list.html"
    context_object_name = "exams"
    paginate_by = 20
    permission_field = "can_manage_exams"

    def get_queryset(self):
        qs = (
            self.get_school_exams_queryset()
            .annotate(
                questions_count=Count("question", distinct=True),
                reports_count=Count("reports", distinct=True),
                calc_avg_score=Avg("reports__score"),
                calc_avg_pct=Avg("reports__percentage"),
            )
            .order_by("-sort_number", "-pk")
        )
        q = (self.request.GET.get("q") or "").strip()
        status = (self.request.GET.get("status") or "").strip()
        grade_id = (self.request.GET.get("grade") or "").strip()
        lesson_id = (self.request.GET.get("lesson") or "").strip()
        active_filter = (self.request.GET.get("active") or "").strip()

        if q:
            qs = qs.filter(Q(name__icontains=q) | Q(section__icontains=q))
        if status:
            qs = qs.filter(status=status)
        if grade_id.isdigit():
            qs = qs.filter(grade_id=int(grade_id))
        if lesson_id.isdigit():
            qs = qs.filter(lesson_id=int(lesson_id))
        if active_filter == "active":
            qs = qs.filter(is_active=True)
        elif active_filter == "inactive":
            qs = qs.filter(is_active=False)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["grades"] = GradeCategories.objects.filter(is_active=True)
        ctx["lessons"] = LessonCategories.objects.filter(is_active=True)
        ctx["exam_statuses"] = Exam.ExamStatus.choices
        return ctx


class ExamCreateView(ManagerMixin, TemplateView):
    template_name = "manager/exams/exam_form.html"
    permission_field = "can_manage_exams"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["is_edit"] = False
        if "form" not in ctx:
            ctx["form"] = ManagerExamForm(school=self.get_school())
        return ctx

    def post(self, request, *args, **kwargs):
        school = self.get_school()
        form = ManagerExamForm(request.POST, request.FILES, school=school)
        if form.is_valid():
            exam = form.save(commit=False)
            exam.school = school
            exam.province = school.province
            exam.city = school.city
            exam.save()
            form.save_m2m()
            messages.success(request, f"آزمون «{exam.name}» با موفقیت ایجاد شد.")
            return redirect("manager:exam-list")
        messages.error(request, "لطفاً اطلاعات فرم آزمون را بررسی کنید.")
        return self.render_to_response(self.get_context_data(form=form))


class ExamUpdateView(ManagerMixin, TemplateView):
    template_name = "manager/exams/exam_form.html"
    permission_field = "can_manage_exams"

    def get_exam(self):
        return get_object_or_404(
            self.get_school_exams_queryset(), pk=self.kwargs["pk"]
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        exam = self.get_exam()
        ctx["exam_obj"] = exam
        ctx["is_edit"] = True
        if "form" not in ctx:
            ctx["form"] = ManagerExamForm(instance=exam, school=self.get_school())
        return ctx

    def post(self, request, *args, **kwargs):
        exam = self.get_exam()
        school = self.get_school()
        form = ManagerExamForm(
            request.POST, request.FILES, instance=exam, school=school
        )
        if form.is_valid():
            updated = form.save(commit=False)
            if not updated.school_id:
                updated.school = school
            updated.save()
            form.save_m2m()
            messages.success(request, f"آزمون «{updated.name}» با موفقیت ویرایش شد.")
            return redirect("manager:exam-list")
        messages.error(request, "لطفاً اطلاعات فرم ویرایش آزمون را بررسی کنید.")
        return self.render_to_response(self.get_context_data(form=form))


class ExamStatusActionView(ManagerMixin, View):
    """
    تأیید / رد / تغییر وضعیت یا فعال/غیرفعال‌سازی آزمون توسط مدیر مدرسه (بدون حذف).
    """

    permission_field = "can_manage_exams"

    def post(self, request, pk, *args, **kwargs):
        exam = get_object_or_404(self.get_school_exams_queryset(), pk=pk)
        action = request.POST.get("action", "toggle_active")

        if action == "approve":
            exam.status = Exam.ExamStatus.WAITING_START
            exam.is_active = True
            exam.save(update_fields=["status", "is_active", "updated_at"])
            messages.success(request, f"آزمون «{exam.name}» تأیید و فعال شد.")
        elif action == "reject":
            exam.status = Exam.ExamStatus.CANCELED
            exam.is_active = False
            exam.save(update_fields=["status", "is_active", "updated_at"])
            messages.warning(request, f"آزمون «{exam.name}» رد و غیرفعال شد.")
        elif action == "publish_results":
            exam.status = Exam.ExamStatus.RESULTS_PUBLISHED
            exam.save(update_fields=["status", "updated_at"])
            messages.success(request, f"نتایج آزمون «{exam.name}» منتشر شد.")
        elif action == "set_status":
            form = ManagerExamStatusForm(request.POST)
            if form.is_valid():
                exam.status = form.cleaned_data["status"]
                exam.is_active = bool(form.cleaned_data.get("is_active", exam.is_active))
                exam.save(update_fields=["status", "is_active", "updated_at"])
                messages.success(request, f"وضعیت آزمون «{exam.name}» بروزرسانی شد.")
        else:
            new_state = self.toggle_object_active(exam)
            status_label = "فعال" if new_state else "غیرفعال"
            messages.info(
                request,
                f"وضعیت آزمون «{exam.name}» به «{status_label}» تغییر یافت.",
            )

        return redirect(request.META.get("HTTP_REFERER") or "manager:exam-list")


class ExamAnalyticalDetailView(ManagerMixin, TemplateView):
    template_name = "manager/exams/exam_analytics.html"
    permission_field = "can_manage_exams"

    def get_exam(self):
        return get_object_or_404(
            self.get_school_exams_queryset(), pk=self.kwargs["pk"]
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        exam = self.get_exam()
        school = self.get_school()
        ctx["exam_obj"] = exam

        reports_qs = (
            ExamReport.objects.filter(exam=exam, student__school=school, is_active=True)
            .select_related("student__user", "student__grade", "student__major")
            .order_by("rank", "-percentage")
        )
        stats = reports_qs.aggregate(
            participants=Count("id"),
            avg_score=Avg("score"),
            max_score=Max("score"),
            min_score=Min("score"),
            avg_percentage=Avg("percentage"),
            max_percentage=Max("percentage"),
            min_percentage=Min("percentage"),
            pass_count=Count("id", filter=Q(percentage__gte=50)),
        )
        participants = stats["participants"] or 0
        stats["pass_rate"] = (
            round((stats["pass_count"] / participants) * 100, 1)
            if participants > 0
            else 0
        )
        ctx["exam_stats"] = stats
        ctx["reports"] = reports_qs[:100]

        questions = (
            Question.objects.filter(exam=exam, is_active=True)
            .annotate(
                total_answers=Count(
                    "student_answers",
                    filter=Q(student_answers__student__school=school),
                ),
                correct_answers=Count(
                    "student_answers",
                    filter=Q(
                        student_answers__student__school=school,
                        student_answers__corrected=StudentAnswer.TypeOfCorrect.excellent,
                    )
                    | Q(
                        student_answers__student__school=school,
                        student_answers__selected_option__is_correct=True,
                    ),
                ),
                wrong_answers=Count(
                    "student_answers",
                    filter=Q(
                        student_answers__student__school=school,
                        student_answers__corrected=StudentAnswer.TypeOfCorrect.wrong,
                    ),
                ),
                avg_question_score=Avg(
                    "student_answers__score",
                    filter=Q(student_answers__student__school=school),
                ),
            )
            .order_by("pk")
        )
        question_rows = []
        for idx, q_obj in enumerate(questions, start=1):
            total_ans = q_obj.total_answers or 0
            correct_ans = q_obj.correct_answers or 0
            correct_pct = round((correct_ans / total_ans) * 100, 1) if total_ans else 0
            question_rows.append(
                {
                    "index": idx,
                    "question": q_obj,
                    "total_answers": total_ans,
                    "correct_answers": correct_ans,
                    "wrong_answers": q_obj.wrong_answers or 0,
                    "correct_pct": correct_pct,
                    "avg_score": round(q_obj.avg_question_score or 0, 2),
                }
            )
        ctx["question_rows"] = question_rows
        return ctx


# ============================================================
# مدیریت تمرین‌های مدرسه (Practices)
# ============================================================
class PracticeListView(ManagerMixin, ListView):
    template_name = "manager/exams/practice_list.html"
    context_object_name = "practices"
    paginate_by = 20
    permission_field = "can_manage_exams"

    def get_queryset(self):
        qs = (
            self.get_school_practices_queryset()
            .annotate(
                questions_count=Count("question", distinct=True),
                submissions_count=Count("student_details", distinct=True),
                avg_score=Avg("student_details__score"),
            )
            .order_by("-sort_number", "-pk")
        )
        q = (self.request.GET.get("q") or "").strip()
        status = (self.request.GET.get("status") or "").strip()
        if q:
            qs = qs.filter(
                Q(name__icontains=q) | Q(section__klass__name__icontains=q)
            )
        if status == "active":
            qs = qs.filter(is_active=True)
        elif status == "inactive":
            qs = qs.filter(is_active=False)
        return qs


class PracticeCreateView(ManagerMixin, TemplateView):
    template_name = "manager/exams/practice_form.html"
    permission_field = "can_manage_exams"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["is_edit"] = False
        if "form" not in ctx:
            ctx["form"] = ManagerPracticeForm(school=self.get_school())
        return ctx

    def post(self, request, *args, **kwargs):
        school = self.get_school()
        form = ManagerPracticeForm(request.POST, school=school)
        if form.is_valid():
            practice = form.save(commit=False)
            practice.creator = request.user
            practice.save()
            form.save_m2m()
            messages.success(request, f"تمرین «{practice.name}» با موفقیت ایجاد شد.")
            return redirect("manager:practice-list")
        return self.render_to_response(self.get_context_data(form=form))


class PracticeUpdateView(ManagerMixin, TemplateView):
    template_name = "manager/exams/practice_form.html"
    permission_field = "can_manage_exams"

    def get_practice(self):
        return get_object_or_404(
            self.get_school_practices_queryset(), pk=self.kwargs["pk"]
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        practice = self.get_practice()
        ctx["practice_obj"] = practice
        ctx["is_edit"] = True
        if "form" not in ctx:
            ctx["form"] = ManagerPracticeForm(
                instance=practice, school=self.get_school()
            )
        return ctx

    def post(self, request, *args, **kwargs):
        practice = self.get_practice()
        form = ManagerPracticeForm(
            request.POST, instance=practice, school=self.get_school()
        )
        if form.is_valid():
            form.save()
            messages.success(request, f"تمرین «{practice.name}» با موفقیت ویرایش شد.")
            return redirect("manager:practice-list")
        return self.render_to_response(self.get_context_data(form=form))


class PracticeToggleActiveView(ManagerMixin, View):
    permission_field = "can_manage_exams"

    def post(self, request, pk, *args, **kwargs):
        practice = get_object_or_404(self.get_school_practices_queryset(), pk=pk)
        new_state = self.toggle_object_active(practice)
        status_label = "فعال" if new_state else "غیرفعال"
        messages.info(
            request,
            f"وضعیت تمرین «{practice.name}» به «{status_label}» تغییر یافت.",
        )
        return redirect(request.META.get("HTTP_REFERER") or "manager:practice-list")
