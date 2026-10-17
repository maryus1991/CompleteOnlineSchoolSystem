from django.contrib import messages
from django.db import transaction
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from apps.questions.models import Question
from apps.users.teachers.forms.questions import (
    QuestionAnswerKeyForm,
    QuestionForm,
    QuestionOptionFormSet,
    QuestionOptionUpdateFormSet,
)
from apps.users.teachers.mixins import TeacherMixin


class QuestionListView(TeacherMixin, ListView):
    """list the teacher's questions"""

    permission_field = "can_add_question"
    template_name = "teacher/question/list.html"
    context_object_name = "items"
    paginate_by = 100

    def get_queryset(self):
        return Question.objects.filter(
            teacher=self.request.teacher,
            is_active=True,
        ).select_related("grade", "major", "lesson", "answer_key")


class QuestionCreateView(TeacherMixin, CreateView):
    """create a new question with its options and key"""

    permission_field = "can_add_question"
    model = Question
    form_class = QuestionForm
    template_name = "teacher/question/form.html"
    success_url = reverse_lazy("teacher:question-list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context["answer_key_form"] = QuestionAnswerKeyForm(self.request.POST, self.request.FILES)
            context["option_formset"] = QuestionOptionFormSet(self.request.POST, prefix="options")
        else:
            context["answer_key_form"] = QuestionAnswerKeyForm()
            context["option_formset"] = QuestionOptionFormSet(prefix="options")
        context["page_title"] = "ساخت سوال جدید"
        context["page_subtitle"] = "سوال، کلید پاسخ و در صورت نیاز گزینه‌ها را وارد کنید"
        context["is_update"] = False
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        answer_key_form = context["answer_key_form"]
        option_formset = context["option_formset"]

        if not answer_key_form.is_valid():
            messages.error(self.request, "کلید سوال الزامی است و باید به درستی پر شود.")
            return self.render_to_response(self.get_context_data(form=form))

        if not option_formset.is_valid():
            messages.error(self.request, "خطا در گزینه‌های سوال.")
            return self.render_to_response(self.get_context_data(form=form))

        with transaction.atomic():
            form.instance.teacher = self.request.teacher
            self.object = form.save()

            answer_key = answer_key_form.save(commit=False)
            answer_key.question = self.object
            answer_key.save()

            option_formset.instance = self.object
            options = option_formset.save(commit=False)
            for option in options:
                if option.name and str(option.name).strip():
                    option.question = self.object
                    option.save()
            for obj in option_formset.deleted_objects:
                obj.delete()

        messages.success(self.request, "سوال با موفقیت ثبت شد.")
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        messages.error(self.request, form.errors)
        return super().form_invalid(form)


class QuestionUpdateView(TeacherMixin, UpdateView):
    """update the questions with its options and key"""

    permission_field = "can_add_question"
    model = Question
    form_class = QuestionForm
    template_name = "teacher/question/form.html"
    success_url = reverse_lazy("teacher:question-list")
    context_object_name = "question"

    def get_queryset(self):
        return Question.objects.filter(
            teacher=self.request.teacher,
            is_active=True,
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        question = self.object

        if self.request.POST:
            context["answer_key_form"] = QuestionAnswerKeyForm(
                self.request.POST,
                self.request.FILES,
                instance=getattr(question, "answer_key", None),
            )
            context["option_formset"] = QuestionOptionUpdateFormSet(
                self.request.POST,
                instance=question,
                prefix="options",
            )
        else:
            answer_key_instance = getattr(question, "answer_key", None)
            context["answer_key_form"] = QuestionAnswerKeyForm(instance=answer_key_instance)
            context["option_formset"] = QuestionOptionUpdateFormSet(
                instance=question,
                prefix="options",
            )

        context["page_title"] = "ویرایش سوال"
        context["page_subtitle"] = "متن سوال، کلید پاسخ و گزینه‌ها را ویرایش کنید"
        context["is_update"] = True
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        answer_key_form = context["answer_key_form"]
        option_formset = context["option_formset"]

        if not answer_key_form.is_valid():
            messages.error(self.request, "کلید سوال الزامی است و باید به درستی پر شود.")
            return self.render_to_response(self.get_context_data(form=form))

        if not option_formset.is_valid():
            messages.error(self.request, "خطا در گزینه‌های سوال.")
            return self.render_to_response(self.get_context_data(form=form))

        with transaction.atomic():
            self.object = form.save()

            answer_key = answer_key_form.save(commit=False)
            answer_key.question = self.object
            answer_key.save()

            option_formset.instance = self.object
            options = option_formset.save(commit=False)
            for option in options:
                if option.name and str(option.name).strip():
                    option.question = self.object
                    option.save()
            for obj in option_formset.deleted_objects:
                obj.delete()

        messages.success(self.request, "تغییرات سوال ذخیره شد.")
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        messages.error(self.request, form.errors)
        return super().form_invalid(form)


class QuestionDeleteView(TeacherMixin, DeleteView):
    """soft delete with is_active=False"""

    permission_field = "can_add_question"
    model = Question
    template_name = "teacher/question/confirm_delete.html"
    success_url = reverse_lazy("teacher:question-list")
    context_object_name = "question"

    def get_queryset(self):
        return Question.objects.filter(
            teacher=self.request.teacher,
            is_active=True,
        )

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.is_active = False
        self.object.save(update_fields=["is_active"])
        messages.warning(request, "سوال حذف شد (غیرفعال گردید برای برگردوندن ان با ادمین در تماس باشید).")
        return HttpResponseRedirect(self.get_success_url())

 
    def form_valid(self, form):
        return self.delete(self.request)
