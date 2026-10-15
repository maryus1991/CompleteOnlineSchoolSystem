from django.contrib import admin
from .models import GradeCategories, MajorCategories,  BlogCategories, LessonCategories


# Register your models here.

admin.site.register(MajorCategories)
admin.site.register(GradeCategories)
admin.site.register(LessonCategories)

admin.site.register(BlogCategories)