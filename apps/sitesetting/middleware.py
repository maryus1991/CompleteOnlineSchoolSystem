
from .models import Site


from django.utils.deprecation import MiddlewareMixin
from django.utils.functional import SimpleLazyObject

class SiteMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request.site = SimpleLazyObject(lambda: Site.objects.filter(is_active=True).first())