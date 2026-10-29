from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from debug_toolbar.toolbar import debug_toolbar_urls
from django.conf.urls import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.sitesetting.urls')),
    path('posts/', include('apps.article.urls')),
    path('courses/', include('apps.classes.urls')),
    path('users/', include('apps.users.accounts.urls')),
    path('exams/', include('apps.exams.urls')),
    path('qbank/', include('apps.questions.urls')),
    path('student/', include('apps.users.students.urls')),
    path('teacher/', include('apps.users.teachers.urls')),
    path('adviser/', include('apps.users.advisers.urls')),
    path("ckeditor5/", include('django_ckeditor_5.urls')),
]

if settings.DEBUG:
    urlpatterns += debug_toolbar_urls() + static.static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
