from django.contrib import messages
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.timezone import now
from django.views import View
from django.views.generic import CreateView, DeleteView, ListView, UpdateView
from apps.progress.models import StudyPlan, StudyPlanItem, DailyStudyLog
from apps.users.advisers.forms.daily_log import DailyLogReviewForm
from apps.users.advisers.forms.study_plan import (
    StudyPlanForm,
    StudyPlanItemFormSet,
)
from apps.users.advisers.mixins import AdviserMixin


class StudyPlanListView(AdviserMixin, ListView):
    """adviser student study plan list"""
    permission_field = "can_manage_study_plans"
    template_name = "adviser/plans/list.html"
    context_object_name = "items"
    paginate_by = 50

    def get_queryset(self):
        students_qs = self.get_adviser_students_queryset()
        qs = (
            StudyPlan.objects.filter(
                student__in=students_qs,
                is_active=True,
            )
            .select_related("student", "student__user", "adviser", "adviser__user")
            .prefetch_related("items")
            .order_by("-start_date", "-pk")
        )
        student_id = self.request.GET.get("student")
        status = self.request.GET.get("status")
        if student_id and student_id.isdigit():
            qs = qs.filter(student_id=int(student_id))
        if status:
            qs = qs.filter(status=status)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["students"] = self.get_adviser_students_queryset()
        ctx["statuses"] = StudyPlan.Status.choices
        ctx["selected_student"] = self.request.GET.get("student", "")
        ctx["selected_status"] = self.request.GET.get("status", "")
        return ctx


class StudyPlanCreateView(AdviserMixin, CreateView):
    """study plane creation"""
    permission_field = "can_manage_study_plans"
    model = StudyPlan
    form_class = StudyPlanForm
    template_name = "adviser/plans/form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["adviser"] = self.request.adviser
        return kwargs

    def get_initial(self):
        initial = super().get_initial()
        student_id = self.request.GET.get("student")
        if student_id and student_id.isdigit():
            initial["student"] = int(student_id)
        return initial

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["page_title"] = "تعریف برنامه مطالعاتی جدید"
        ctx["page_subtitle"] = "طراحی برنامه هفتگی یا دوره‌ای برای دانش‌آموز"
        ctx["is_update"] = False
        return ctx

    def form_valid(self, form):
        student = form.cleaned_data["student"]
        if not self.get_adviser_students_queryset().filter(pk=student.pk).exists():
            messages.error(self.request, "این دانش‌آموز تحت پوشش شما نیست.")
            return self.form_invalid(form)

        form.instance.adviser = self.request.adviser
        if not form.instance.sort_number:
            form.instance.sort_number = 1
        self.object = form.save()
        messages.success(self.request, "برنامه مطالعاتی ایجاد شد. اکنون باکس‌های هفتگی را تنظیم کنید.")
        return HttpResponseRedirect(
            reverse("adviser:plan-items", kwargs={"pk": self.object.pk})
        )

    def form_invalid(self, form):
        messages.error(self.request, "لطفاً خطاهای فرم برنامه مطالعاتی را بررسی کنید.")
        return super().form_invalid(form)


class StudyPlanUpdateView(AdviserMixin, UpdateView):
    """update study plan"""
    permission_field = "can_manage_study_plans"
    model = StudyPlan
    form_class = StudyPlanForm
    template_name = "adviser/plans/form.html"
    context_object_name = "plan"

    def get_queryset(self):
        return StudyPlan.objects.filter(
            student__in=self.get_adviser_students_queryset(),
            is_active=True,
        ).select_related("student", "student__user")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["adviser"] = self.request.adviser
        return kwargs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["page_title"] = "ویرایش برنامه مطالعاتی"
        ctx["page_subtitle"] = f"{self.object.title} — {self.object.student}"
        ctx["is_update"] = True
        return ctx

    def get_success_url(self):
        return reverse("adviser:plan-list")

    def form_valid(self, form):
        student = form.cleaned_data["student"]
        if not self.get_adviser_students_queryset().filter(pk=student.pk).exists():
            messages.error(self.request, "این دانش‌آموز تحت پوشش شما نیست.")
            return self.form_invalid(form)
        if not form.instance.sort_number:
            form.instance.sort_number = 1
        messages.success(self.request, "تغییرات برنامه مطالعاتی ذخیره شد.")
        return super().form_valid(form)


class StudyPlanDeleteView(AdviserMixin, DeleteView):
    """soft delete of study plan"""
    permission_field = "can_manage_study_plans"
    model = StudyPlan
    template_name = "adviser/plans/confirm_delete.html"
    context_object_name = "plan"
    success_url = reverse_lazy("adviser:plan-list")

    def get_queryset(self):
        return StudyPlan.objects.filter(
            student__in=self.get_adviser_students_queryset(),
            is_active=True,
        ).select_related("student", "student__user")

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.is_active = False
        self.object.save(update_fields=["is_active"])
        messages.warning(request, "برنامه مطالعاتی غیرفعال و حذف شد.")
        return HttpResponseRedirect(self.success_url)

    def form_valid(self, form):
        return self.delete(self.request)


class StudyPlanItemsManageView(AdviserMixin, View):
    """manage the study plan items by formset"""
    permission_field = "can_manage_study_plans"
    template_name = "adviser/plans/items_manage.html"

    def get_plan(self):
        return get_object_or_404(
            StudyPlan.objects.filter(
                student__in=self.get_adviser_students_queryset(),
                is_active=True,
            ).select_related("student", "student__user"),
            pk=self.kwargs["pk"],
        )

    def _group_items_by_day(self, plan):
        items = (
            plan.items.filter(is_active=True)
            .select_related("lesson")
            .order_by("day_of_week", "sort_number", "pk")
        )
        grouped = {day_val: {"label": day_label, "items": []} for day_val, day_label in StudyPlanItem.DayOfWeek.choices}
        for item in items:
            if item.day_of_week in grouped:
                grouped[item.day_of_week]["items"].append(item)
        return grouped

    def get(self, request, *args, **kwargs):
        plan = self.get_plan()
        formset = StudyPlanItemFormSet(
            instance=plan,
            queryset=StudyPlanItem.objects.filter(study_plan=plan, is_active=True).select_related("lesson"),
            prefix="items",
        )
        return render(
            request,
            self.template_name,
            {
                "plan": plan,
                "formset": formset,
                "days_grouped": self._group_items_by_day(plan),
            },
        )

    def post(self, request, *args, **kwargs):
        plan = self.get_plan()
        formset = StudyPlanItemFormSet(
            request.POST,
            instance=plan,
            queryset=StudyPlanItem.objects.filter(study_plan=plan, is_active=True).select_related("lesson"),
            prefix="items",
        )
        if formset.is_valid():
            with transaction.atomic():
                instances = formset.save(commit=False)
                for inst in instances:
                    inst.study_plan = plan
                    if not inst.sort_number:
                        inst.sort_number = 1
                    inst.save()
                for deleted in formset.deleted_objects:
                    deleted.delete()
            messages.success(request, "باکس‌های مطالعاتی هفته با موفقیت بروزرسانی شدند.")
            return redirect("adviser:plan-items", pk=plan.pk)

        messages.error(request, "لطفاً اطلاعات باکس‌های مطالعاتی را بررسی کنید.")
        return render(
            request,
            self.template_name,
            {
                "plan": plan,
                "formset": formset,
                "days_grouped": self._group_items_by_day(plan),
            },
        )


class DailyLogReviewListView(AdviserMixin, ListView):
    """student daily log list  """
    permission_field = "can_manage_study_plans"
    template_name = "adviser/logs/list.html"
    context_object_name = "items"
    paginate_by = 50

    def get_queryset(self):
        qs = (
            DailyStudyLog.objects.filter(
                student__in=self.get_adviser_students_queryset(),
                is_active=True,
            )
            .select_related(
                "student",
                "student__user",
                "lesson",
                "study_plan_item",
                "study_plan_item__study_plan",
            )
            .order_by("-log_date", "-pk")
        )
        status = self.request.GET.get("status")
        student_id = self.request.GET.get("student")
        if status:
            qs = qs.filter(review_status=status)
        if student_id and student_id.isdigit():
            qs = qs.filter(student_id=int(student_id))
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["students"] = self.get_adviser_students_queryset()
        ctx["statuses"] = DailyStudyLog.ReviewStatus.choices
        ctx["selected_status"] = self.request.GET.get("status", "")
        ctx["selected_student"] = self.request.GET.get("student", "")
        return ctx


class DailyLogReviewActionView(AdviserMixin, View):
    """set action for student daily log """
    permission_field = "can_send_adviser_notes"

    def post(self, request, *args, **kwargs):
        log_obj = get_object_or_404(
            DailyStudyLog.objects.filter(
                student__in=self.get_adviser_students_queryset(),
                is_active=True,
            ),
            pk=kwargs["pk"],
        )
        form = DailyLogReviewForm(request.POST, instance=log_obj)
        if form.is_valid():
            updated = form.save(commit=False)
            updated.reviewed_at = now()
            updated.save(update_fields=["review_status", "adviser_feedback", "reviewed_at"])
            messages.success(request, "بازخورد مشاور روی گزارش کار ثبت شد.")
        else:
            messages.error(request, "خطا در ثبت بازخورد گزارش کار.")
        next_url = request.POST.get("next") or reverse("adviser:daily-log-list")
        return redirect(next_url)
