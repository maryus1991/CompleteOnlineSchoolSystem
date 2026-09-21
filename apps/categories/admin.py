from django.contrib import admin
from .models import GradeCategories, MajorCategories, ProvinceCategories, CityCategories


# Register your models here.


admin.site.register(GradeCategories)
admin.site.register(MajorCategories)
admin.site.register(ProvinceCategories)
admin.site.register(CityCategories)