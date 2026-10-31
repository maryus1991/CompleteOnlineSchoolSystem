from django.contrib import admin
from apps.users.accounts.models import User
from apps.users.students.models import Student
from apps.users.advisers.models import Adviser

from apps.users.teachers.models import Teacher

# Register your models here.

admin.site.register(User)
admin.site.register(Student)
admin.site.register(Adviser)

admin.site.register(Teacher)