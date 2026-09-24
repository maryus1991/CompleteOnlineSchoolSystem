from django.views.generic import ListView, DetailView
from django.db.models import Count, Exists, OuterRef, Q
from .models import Exam, Student



class ExamListView(ListView):
    """for listing the exams"""

    context_object_name = "items"
    paginate_by = 100
    template_name = "main/exam/list.html"


    def get_queryset(self):
        queryset = Exam.objects.filter(is_active=True, is_public=True).select_related("school", "grade", "major", "lesson", ).annotate(
            student_count=Count('selected_student', distinct=True),
            questions_count=Count('question', distinct=True),
            is_student=Exists(
                Student.objects.filter(
                    user=self.request.user if self.request.user.is_authenticated else None,
                    classes=OuterRef("pk"),
                ))
        )



        if q := self.request.GET.get("q"):
            queryset = queryset.filter(
                Q(school__name__icontains=q) |
                Q(grade__name__icontains=q) |
                Q(major__name__icontains=q) |
                Q(lesson__name__icontains=q) |
                Q(summery__icontains=q) |
                Q(description__icontains=q) |
                Q(name__icontains=q) |
                Q(section__icontains=q)
        )


        return queryset


class ExamDetailsView(DetailView):
    """for details exam"""
    context_object_name = 'object'
    template_name = 'main/exam/details.html'

    def get_queryset(self) :
        queryset = Exam.objects.filter(
            is_active=True,
            is_public=True,
        ).select_related("grade", "major", "lesson", ).annotate(
            student_count=Count('selected_student', distinct=True),
            questions_count=Count('question', distinct=True),
            is_student=Exists(
                Student.objects.filter(
                    user=self.request.user if self.request.user.is_authenticated else None,
                    classes=OuterRef("pk"),
                ))
        )
        return queryset

    def get_context_data(self, *args, **kwargs):
        data = super().get_context_data(*args, **kwargs)
        data.update(
            {

                "related": Exam.objects.filter(
                    Q(lesson=self.object.lesson)|
                    Q(major=self.object.major)|
                    Q(grade=self.object.grade),
                    is_active=True,
                    is_public=True,
                ).annotate(
                    student_count=Count('selected_student', distinct=True),
                    questions_count=Count('question', distinct=True),
                    is_student=Exists(
                        Student.objects.filter(
                            user=self.request.user if self.request.user.is_authenticated else None,
                            classes=OuterRef("pk"),
                        )
                    ),
                ).select_related("grade", "major", "lesson")
                .exclude(id=self.object.id)[:self.request.site.count_of_courses_in_course_detail_page],
            }
        )
        return data
