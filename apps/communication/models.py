from django.db import models
from apps.common.models import BaseModel
from apps.classes.models import Class
from apps.users.students.models import Student
from apps.users.teachers.models import Teacher

class ClassMessage(BaseModel):
    klass = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='message', verbose_name="کلاس")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='message', null=True, blank=True, verbose_name="دانش اموز")
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='message', null=True, blank=True, verbose_name="معلم")
    content = models.TextField("متن")


    class Meta:
        ordering = ['pk']
        verbose_name = 'پیام کلاس'
        verbose_name_plural = 'پیام های کلاسی'
