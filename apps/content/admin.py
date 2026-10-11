from django.contrib import admin
from .models import ClassArticle, ClassFile, Section
# Register your models here.

admin.site.register(Section)

admin.site.register(ClassArticle)
admin.site.register(ClassFile)
