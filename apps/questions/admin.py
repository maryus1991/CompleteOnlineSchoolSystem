from django.contrib import admin

from .models import Question, QuestionOption, QuestionAnswerKey, StudentAnswer

admin.site.register(Question)
admin.site.register(QuestionOption)
admin.site.register(QuestionAnswerKey)
admin.site.register(StudentAnswer)

