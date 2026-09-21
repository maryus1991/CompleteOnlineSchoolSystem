# from apps.common.models import BaseModel
# from django.db import models
#
# class StudentReport(BaseModel):
#     class ReportStatus(models.TextChoices):
#         not_corrected = 'تصحیح نشده', 'تصحیح نشده'
#         weak = 'نیاز به تلاش بیشتر', 'نیاز به تلاش بیشتر'
#         average = 'متوسط', 'متوسط'
#         good = 'خوب', 'خوب'
#         excellent = 'عالی', 'عالی'
#
#     user = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='کاربر', related_name='reports',db_index=True)
#     quiz = models.ForeignKey(Quiz, on_delete=models.PROTECT, verbose_name='ازمون', related_name='reports',db_index=True)
#     grade = models.ForeignKey(GradeCategories, null=True, blank=True, related_name='reports', on_delete=models.PROTECT,verbose_name='پایه', db_index=True)
#     major = models.ForeignKey(MajorCategories, null=True, blank=True, related_name='reports', on_delete=models.PROTECT,verbose_name='رشته تحصیلی', db_index=True)
#     lesson = models.ForeignKey(LessionCategories, null=True, blank=True, related_name='reports', on_delete=models.PROTECT, verbose_name='درس', db_index=True)
#
#     score = models.IntegerField(verbose_name='نمره')
#     percent = models.IntegerField(verbose_name='درصد')
#     teraze = models.PositiveIntegerField(verbose_name='تراز', default=0)
#     order = models.PositiveIntegerField(verbose_name='رتبه', default=0)
#     status = models.CharField(max_length=100, choices=ReportStatus.choices, verbose_name='وضعیت عملکردی',default=ReportStatus.not_corrected)
#     created_at = models.DateTimeField(auto_now_add=True)  # time to answer
#
#     def __str__(self):
#         return f'{self.quiz.name} - {str(self.user.PhoneNumber).replace(" ", "")} - {self.teraze} - {self.percent} - {self.score} - {self.status}'
#
#     class Meta:
#
#         verbose_name = 'کارنامه '
#         verbose_name_plural = 'کارنامه ها'
#         unique_together = ('quiz', 'user')
#
#
# class StudentReport(BaseModel):
#     class ReportStatus(models.TextChoices):
#         not_corrected = 'تصحیح نشده', 'تصحیح نشده'
#         weak = 'نیاز به تلاش بیشتر', 'نیاز به تلاش بیشتر'
#         average = 'متوسط', 'متوسط'
#         good = 'خوب', 'خوب'
#         excellent = 'عالی', 'عالی'
#
#     user = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='کاربر', related_name='reports',db_index=True)
#     quiz = models.ForeignKey(Quiz, on_delete=models.PROTECT, verbose_name='ازمون', related_name='reports',db_index=True)
#     grade = models.ForeignKey(GradeCategories, null=True, blank=True, related_name='reports', on_delete=models.PROTECT,verbose_name='پایه', db_index=True)
#     major = models.ForeignKey(MajorCategories, null=True, blank=True, related_name='reports', on_delete=models.PROTECT,verbose_name='رشته تحصیلی', db_index=True)
#     lesson = models.ForeignKey(LessionCategories, null=True, blank=True, related_name='reports', on_delete=models.PROTECT, verbose_name='درس', db_index=True)
#
#     score = models.IntegerField(verbose_name='نمره')
#     percent = models.IntegerField(verbose_name='درصد')
#     teraze = models.PositiveIntegerField(verbose_name='تراز', default=0)
#     order = models.PositiveIntegerField(verbose_name='رتبه', default=0)
#     status = models.CharField(max_length=100, choices=ReportStatus.choices, verbose_name='وضعیت عملکردی',
#                               default=ReportStatus.not_corrected)
#     created_at = models.DateTimeField(auto_now_add=True)  # time to answer
#
#     def __str__(self):
#         return f'{self.quiz.name} - {str(self.user.PhoneNumber).replace(" ", "")} - {self.teraze} - {self.percent} - {self.score} - {self.status}'
#
#     class Meta:
#         ordering = ["order", "-teraze", "-percent", "-score", ]
#         verbose_name = 'کارنامه '
#         verbose_name_plural = 'کارنامه ها'
#         unique_together = ('quiz', 'user')