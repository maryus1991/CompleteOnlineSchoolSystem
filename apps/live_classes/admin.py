from django.contrib import admin
from .models import StreamServers, LiveClass, LiveClassRequest

admin.site.register(LiveClassRequest)
admin.site.register(StreamServers)
admin.site.register(LiveClass)
