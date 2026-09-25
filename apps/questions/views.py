
from django.db.models import Q
from django.views.generic import ListView

from .models import Question
from apps.categories.models import (
    GradeCategories,
    MajorCategories,
    LessonCategories,
)


class QuestionBankListView(ListView):
    """
    نمایش بانک سوالات

    فیلترها:
        ?q=
        ?major=
        ?grade=
        ?lesson=
    """

    model = Question
    template_name = "main/qbank/list.html"
    context_object_name = "questions"
    paginate_by = 10

    def dispatch(self, request, *args, **kwargs) :
        if not request.site.qbank_active:
            messages.error(request, "این صفحه غیر فعال میباشد")
            return redirect("site:main")
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = (
            Question.objects
            .filter(is_for_qbank=True)
            .select_related(
                "grade",
                "major",
                "lesson",
                "answer_key",
            )
            .prefetch_related(
                "options",
            )
            .order_by("-sort_number", "-id")
        )

        search = self.request.GET.get("q", "").strip()

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search)
                | Q(description__icontains=search)
            )

        major = self.request.GET.get("major")

        if major:
            queryset = queryset.filter(
                major_id=major
            )

        grade = self.request.GET.get("grade")

        if grade:
            queryset = queryset.filter(
                grade_id=grade
            )

        lesson = self.request.GET.get("lesson")

        if lesson:
            queryset = queryset.filter(
                lesson_id=lesson
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["majors"] = (
            MajorCategories.objects.all()
        )

        context["grades"] = (
            GradeCategories.objects.all()
        )

        context["lessons"] = (
            LessonCategories.objects.all()
        )

        return context

