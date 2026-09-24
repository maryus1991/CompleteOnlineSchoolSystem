from django.views.generic import ListView, DetailView
from apps.classes.models import Class, GradeCategories, MajorCategories, LessonCategories, Student
from django.db.models import Q, Exists, Count, OuterRef, Value, BooleanField

class ClassListView(ListView):
    """for list classes as course"""

    context_object_name = 'items'
    paginate_by = 100
    template_name = 'main/courses/list.html'

    def get_queryset(self):

        if self.request.user.is_authenticated:
            is_student = Exists(
                Student.objects.filter(
                    user=self.request.user,
                    classes=OuterRef("pk"),
                )
            )
        else:
            is_student = Value(
                False,
                output_field=BooleanField(),
            )


        queryset = (
            Class.objects
            .filter(
                is_active=True,
                teacher__is_active=True,
                lesson__is_active=True,
                major__is_active=True,
                grade__is_active=True,
                is_public=True,
            )
            .annotate(
                student_count=Count("student", distinct=True),
                section_count=Count("sections", distinct=True),
                is_student=is_student,
            )
            .select_related(
                "school",
                "teacher",
                "grade",
                "major",
                "lesson",
            )
        )
        if q := self.request.GET.get("q"):

            queryset = queryset.filter(
                Q(school__name__icontains=q) |
                Q(teacher__user__first_name__icontains=q) |
                Q(teacher__user__last_name__icontains=q) |
                Q(grade__name__icontains=q) |
                Q(major__name__icontains=q) |
                Q(lesson__name__icontains=q) |
                Q(summery__icontains=q) |
                Q(first_tag__icontains=q) |
                Q(second_tag__icontains=q) |
                Q(third_tag__icontains=q) |
                Q(name__icontains=q)
            )

        return queryset.distinct()

    def get_context_data(self, *args, **kwargs):
        data = super().get_context_data(*args, **kwargs)
        data.update(
            {
                # "major": MajorCategories.objects.filter(is_active=True),
                # "grade": GradeCategories.objects.filter(is_active=True),
                # "lesson": LessonCategories.objects.filter(is_active=True),
            }
        )
        return data

class ClassDetailView(DetailView):
    """for detail class"""
    context_object_name = 'object'
    template_name = 'main/courses/details.html'

    def get_queryset(self) :
        queryset = Class.objects.filter(
            is_active=True,
            teacher__is_active=True,
            lesson__is_active=True,
            major__is_active=True,
            grade__is_active=True,
            is_public=True,
        ).annotate(
            student_count=Count('student', distinct=True),
            section_count=Count('sections', distinct=True),
            is_student=Exists(
                Student.objects.filter(
                    user=self.request.user if self.request.user.is_authenticated else None,
                    classes=OuterRef("pk"),
                )
            ),
        ).select_related("school", "teacher", "grade", "major", "lesson").prefetch_related("sections")
        return queryset.distinct()

    def get_context_data(self, *args, **kwargs):
        data = super().get_context_data(*args, **kwargs)
        data.update(
            {
                "sections":self.object.sections.filter(is_active=True, is_publish=True).all(),
                "related": Class.objects.filter(
                    Q(lesson=self.object.lesson)|
                    Q(major=self.object.major)|
                    Q(grade=self.object.grade),
                    is_active=True,
                    is_public=True,
                ).annotate(
                    student_count=Count('student', distinct=True),
                    section_count=Count('sections', distinct=True),
                    is_student=Exists(
                        Student.objects.filter(
                            user=self.request.user if self.request.user.is_authenticated else None,
                            classes=OuterRef("pk"),
                        )
                    ),
                ).select_related("teacher", "grade", "major", "lesson")
                .exclude(id=self.object.id)[:self.request.site.count_of_courses_in_course_detail_page],
            }
        )
        return data