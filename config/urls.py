from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from django.db import connections
from django.core.cache import caches


def healthz_view(request):
    db_ok = True
    cache_ok = True

    try:
        with connections["default"].cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
    except Exception:
        db_ok = False

    try:
        caches["default"].set("healthcheck_ping", "ok", timeout=10)
        cache_ok = caches["default"].get("healthcheck_ping") == "ok"
    except Exception:
        cache_ok = False

    status_code = 200 if db_ok else 503
    return JsonResponse(
        {
            "status": "ok" if db_ok else "degraded",
            "database": db_ok,
            "cache": cache_ok,
            "orm_cache_enabled": getattr(settings, "CACHALOT_ENABLED", False),
        },
        status=status_code,
    )


urlpatterns = [
    path('healthz/', healthz_view, name='healthz'),
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
    from debug_toolbar.toolbar import debug_toolbar_urls
    urlpatterns = debug_toolbar_urls() + urlpatterns
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)