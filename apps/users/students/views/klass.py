from apps.classes.models import Class
from apps.content.models import Section
from apps.live_classes.models import LiveClass
from django.shortcuts import get_object_or_404
from django.views.generic import ListView, DetailView
from apps.users.students.mixins import StudentMixin


class LiveClassListView(StudentMixin, ListView):
    """for list live classes """

    model = LiveClass
    template_name = "dashboard/class/live-classes-list.html"
    context_object_name = "live_classes"


    def get_queryset(self):

        live_classes = (
            LiveClass.objects
            .filter(
                status=LiveClass.Status.LIVE,
                section__klass__student=self.request.student,
                section__is_publish=True,
                )
            .select_related("server", "section")
            .order_by("-pk")
        )
        return live_classes

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)

        data.update({
            "student": self.request.user
        })

        return data


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
            Class.objects.filter(student__user=self.request.user, is_active=True).distinct(),
            pk=self.kwargs["pk"],
        )
        return Section.objects.filter(
            klass=self.klass,
            is_publish=True,
            is_active=True,
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
                is_active=True,
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
            .filter(creator__isnull=False, is_active=True)
            .distinct()
        )

        context["live_classes"] = section.live.select_related(
            "server",
            "section__klass__teacher__user",
        ).all()



        return context