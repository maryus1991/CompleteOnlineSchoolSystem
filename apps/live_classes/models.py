from django.db import models
from apps.common.models import BaseModel
from apps.classes.models import Class
from apps.users.students.models import Student
from apps.users.teachers.models import Teacher
from urllib.parse import urljoin



class StreamServers(BaseModel):
    name = models.CharField(verbose_name='عنوان', max_length=255)
    base_url = models.URLField("لینک")
    server_stats_check = models.CharField(verbose_name='مسیر چک کردن منابع', max_length=255, default='/monitor/stats')
    teacher_url_name = models.CharField(verbose_name='مسیر لینک برای استاد', max_length=255, default='/teacher.html')
    TEACHER_KEY = models.CharField(verbose_name='کلید ورود استاد', max_length=255)
    student_url_name = models.CharField(verbose_name='مسیر لینک برای دانش اموز', max_length=255, default='/student.html')
    MONITOR_TOKEN = models.CharField(verbose_name='توکن مانیتور کردن سرور', max_length=255)

    @property
    def monitor_url(self):
        return urljoin(f'{self.base_url.rstrip("/")}/', self.server_stats_check.lstrip('/') ) + f'?token={self.MONITOR_TOKEN}'

    @property
    def teacher_url(self):
        return urljoin(f'{self.base_url.rstrip("/")}/', self.teacher_url_name.lstrip('/') )

    @property
    def student_url(self):
        return urljoin(f'{self.base_url.rstrip("/")}/', self.student_url_name.lstrip('/') )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-pk']
        verbose_name = 'سرور کلاس انلاین'
        verbose_name_plural = 'سرور های کلاس های انلاین'



class LiveClass(BaseModel):
    klass = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='live', verbose_name="کلاس")
    server = models.ForeignKey(StreamServers, on_delete=models.CASCADE, related_name='live', verbose_name="سرور")
    student = models.ManyToManyField(Student, related_name='live', verbose_name="دانش اموز")
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='live', null=True, blank=True, verbose_name="معلم")
    content = models.TextField("متن")

    class Meta:
        ordering = ['pk']
        verbose_name = 'کلاس انلاین'
        verbose_name_plural = 'کلاس های انلاین'
