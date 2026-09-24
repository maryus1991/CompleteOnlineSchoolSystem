from django.contrib import admin
from .models import ClassPractice, ClassArticle, ClassFile, Section
# Register your models here.

admin.site.register(Section)
admin.site.register(ClassPractice)
admin.site.register(ClassArticle)
admin.site.register(ClassFile)
