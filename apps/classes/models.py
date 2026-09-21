from django.db import models
from apps.schools.models import School
from apps.users.students.models import Student
from apps.users.teachers.models import Teacher

class Class(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='classes', verbose_name="مدرسه")
    student = models.ManyToManyField(Student, related_name='classes', verbose_name="دانش اموزان")
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='classes', verbose_name="معلم")
    name = models.CharField("نام", max_length=100)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-pk']
        verbose_name = 'کلاس'
        verbose_name_plural = 'کلاس ها'