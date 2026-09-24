from django.views.generic import ListView
from .models import User


class UserListView(ListView):
    queryset = User.objects.filter(is_active=True, publish=True)
    context_object_name = "items"
    paginate_by = 100
    template_name = "main/teachers/list.html"
