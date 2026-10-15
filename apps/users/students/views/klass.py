from apps.classes.models import Class
from apps.content.models import Section

from django.shortcuts import get_object_or_404
from django.views.generic import ListView, DetailView
from apps.users.students.mixins import StudentMixin



class ListStudentClass(StudentMixin, ListView):
    """ for list student classes """

    model = Class
    template_name = "dashboard/class/list.html"
    context_object_name = "classes"
    paginate_by = 48

    def get_queryset(self):
        return (
        Class.objects
            .filter(student=self.request.student)
            .select_related(
                "school",
                "teacher__user",
                "grade",
                "major",
                "lesson",
            )
            .distinct()
            .order_by("-sort_number", "-pk")
        )

class ListSectionStudentClass(StudentMixin, ListView):
    """ for list student classes """

    model = Section
    template_name = "dashboard/class/sections.html"
    context_object_name = "sections"
    paginate_by = 100


    def get_queryset(self):
        self.klass = get_object_or_404(
            Class.objects.filter(student__user=self.request.user).distinct(),
            pk=self.kwargs["pk"],
        )
        return Section.objects.filter(
            klass=self.klass,
            is_publish=True,
        ).order_by("-sort_number", "pk")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["klass"] = self.klass
        return context

class StudentSectionContentView(StudentMixin, DetailView):
    model = Section
    template_name = "dashboard/class/details.html"
    context_object_name = "section"
    pk_url_kwarg = "section_id"

    def get_queryset(self):
        return (
            Section.objects
            .filter(
                is_publish=True,
                klass__student__user=self.request.user,
                klass_id=self.kwargs["pk"],
            )
            .select_related(
                "klass",
                "klass__school",
                "klass__teacher",
            )
            .prefetch_related(
                "article",
                "file",
                "practices",
                "live__server",

            )
            .distinct()
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        section = self.object

        context["articles"] = section.article.all()
        context["files"] = section.file.all()

        context["practices"] = (
            section.practices
            .filter(creator__isnull=False)
            .distinct()
        )

        context["live_classes"] = section.live.select_related(
            "server",
            "section__klass__teacher__user",
        ).all()



        return context