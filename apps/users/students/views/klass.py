from apps.classes.models import Class
from apps.content.models import Section, ClassArticle, ClassFile
from apps.live_classes.models import LiveClass, StreamServers

from django.views.generic import ListView
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
            .filter(student__user=self.request.user)
            .select_related(
                "school",
                "teacher",
                "grade",
                "major",
                "lesson",
            )
            .distinct()
            .order_by("-sort_number", "-pk")
        )

class ListSectionStudentClass(StudentMixin, ListView):
    """ for list student classes """

    model = Class
    template_name = "dashboard/class/content-list.html"
    context_object_name = "item"
    paginate_by = 48

    def get_queryset(self):
        return
