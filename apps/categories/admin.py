from django.contrib import admin
from .models import GradeCategories, MajorCategories, ProvinceCategories, CityCategories, BlogCategories, LessonCategories


# Register your models here.

admin.site.register(MajorCategories)
admin.site.register(GradeCategories)
admin.site.register(LessonCategories)
admin.site.register(ProvinceCategories)
admin.site.register(CityCategories)
admin.site.register(BlogCategories)