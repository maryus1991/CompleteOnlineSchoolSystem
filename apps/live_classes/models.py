from django.db import models
from apps.common.models import BaseModel
from apps.classes.models import Class
from apps.users.students.models import Student
from apps.users.teachers.models import Teacher


class LiveClass(BaseModel):
    klass = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='live', verbose_name="کلاس")
    student = models.ManyToManyField(Student, related_name='live', verbose_name="دانش اموز")
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='live', null=True, blank=True, verbose_name="معلم")
    content = models.TextField("متن")

    class Meta:
        ordering = ['pk']
        verbose_name = 'کلاس انلاین'
        verbose_name_plural = 'کلاس های انلاین'
