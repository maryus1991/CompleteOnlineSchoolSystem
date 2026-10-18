
from django.shortcuts import get_object_or_404
from django.views.generic import ListView, DetailView

from apps.classes.models import Class
from apps.content.models import Section
from apps.live_classes.models import LiveClass
from apps.users.students.mixins import StudentMixin


class LiveClassListView(StudentMixin, ListView):
    """
    فهرست جلسات آنلاین در حال برگزاری دانش‌آموز.

    دانش‌آموز فقط جلسات کلاس‌هایی را می‌بیند که عضو آن‌هاست.
    ورود به جلسه از صفحه جزئیات همان جلسه انجام می‌شود.
    """

    model = LiveClass
    template_name = "dashboard/class/live-classes-list.html"
    context_object_name = "live_classes"
    paginate_by = 24

    def get_queryset(self):
        return (
            LiveClass.objects
            .filter(
                is_active=True,
                status=LiveClass.Status.LIVE,
                server__is_active=True,
                klass__is_active=True,
                klass__student=self.request.student,
            )
            .select_related(
                "klass",
                "klass__teacher",
                "klass__teacher__user",
                "klass__school",
                "server",
            )
            .order_by("-pk")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["student"] = self.request.student
        return context


class LiveClassDetailView(StudentMixin, DetailView):
    """
    جزئیات یک جلسه آنلاین.

    دسترسی فقط برای دانش‌آموز عضو کلاس مجاز است.
    لینک ورود تنها زمانی ساخته می‌شود که جلسه در حال برگزاری باشد.
    """

    model = LiveClass
    template_name = "dashboard/class/live-class-details.html"
    context_object_name = "live_class"
    pk_url_kwarg = "pk"

    def get_queryset(self):
        return (
            LiveClass.objects
            .filter(
                is_active=True,
                klass__is_active=True,
                klass__student=self.request.student,
                server__is_active=True,
            )
            .select_related(
                "klass",
                "klass__teacher",
                "klass__teacher__user",
                "klass__school",
                "klass__grade",
                "klass__major",
                "klass__lesson",
                "server",
            )
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        live_class = self.object

        context["student"] = self.request.student
        context["meeting_url"] = (
            live_class.get_student_meeting_url(self.request.user)
            if live_class.is_available
            else None
        )

        return context


class ListStudentClass(StudentMixin, ListView):
    """فهرست کلاس‌های درسی دانش‌آموز."""

    model = Class
    template_name = "dashboard/class/list.html"
    context_object_name = "classes"
    paginate_by = 48

    def get_queryset(self):
        return (
            Class.objects
            .filter(
                student=self.request.student,
                is_active=True,
            )
            .select_related(
                "school",
                "teacher__user",
                "grade",
                "major",
                "lesson",
            )
            .order_by("-sort_number", "-pk")
            .distinct()
        )


class ListSectionStudentClass(StudentMixin, ListView):
    """فهرست بخش‌های منتشرشده یک کلاس برای دانش‌آموز."""

    model = Section
    template_name = "dashboard/class/sections.html"
    context_object_name = "sections"
    paginate_by = 100

    def get_queryset(self):
        self.klass = get_object_or_404(
            Class.objects.filter(
                student=self.request.student,
                is_active=True,
            ),
            pk=self.kwargs["pk"],
        )

        return (
            Section.objects
            .filter(
                klass=self.klass,
                is_publish=True,
                is_active=True,
            )
            .order_by("-sort_number", "pk")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["klass"] = self.klass
        return context


class StudentSectionContentView(StudentMixin, DetailView):
    """جزئیات یک بخش از محتوای کلاس دانش‌آموز."""

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
                klass__is_active=True,
                klass__student=self.request.student,
                klass_id=self.kwargs["pk"],
            )
            .select_related(
                "klass",
                "klass__school",
                "klass__teacher",
                "klass__teacher__user",
            )
            .prefetch_related(
                "article",
                "file",
                "practices",
            )
            .distinct()
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        section = self.object

        context["student"] = self.request.student

        context["articles"] = section.article.all()
        context["files"] = section.file.all()

        context["practices"] = (
            section.practices
            .filter(
                creator__isnull=False,
                is_active=True,
            )
            .distinct()
        )

        context["live_classes"] = (
            LiveClass.objects
            .filter(
                klass_id=section.klass_id,
                is_active=True,
                klass__is_active=True,
                klass__student=self.request.student,
                server__is_active=True,
            )
            .select_related(
                "klass",
                "klass__teacher__user",
                "server",
            )
            .order_by("-pk")
        )

        return context
