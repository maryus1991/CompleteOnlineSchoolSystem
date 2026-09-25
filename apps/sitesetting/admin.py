from django.contrib import admin

from .models import Site, Contact, Counseling, FAQ, TestMonomials, TimeLine

admin.site.register(Site)
admin.site.register(Contact)
admin.site.register(Counseling)
admin.site.register(FAQ)
admin.site.register(TestMonomials)
admin.site.register(TimeLine)