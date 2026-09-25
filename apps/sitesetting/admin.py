from django.contrib import admin

from .models import Site, Contact

admin.site.register(Site)
admin.site.register(Contact)