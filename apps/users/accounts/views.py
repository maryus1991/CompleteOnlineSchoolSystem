from django.views.generic import ListView, TemplateView, RedirectView
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .models import User
from .forms import UserLoginForm
from django.urls import reverse_lazy
from django.utils.http import url_has_allowed_host_and_scheme

class UserListView(ListView):
    queryset = User.objects.filter(is_active=True, publish=True)
    context_object_name = "items"
    paginate_by = 100
    template_name = "main/teachers/list.html"


class AuthView(TemplateView):
    """auth view"""
    template_name = "main/auth/auth.html"

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data.update({
            "login_form": UserLoginForm(self.request.POST or None),
            "next": self.request.GET.get("next"),
        })
        return data

class UserLoginView(RedirectView):
    """for login view"""

    def get_redirect_url(self):

        if not self.request.site.login_active:
            messages.error(self.request, "ورود به این صفحه غیرفعال میباشد")
            return reverse_lazy("user:auth")

        data = UserLoginForm(self.request.POST or None)


        if data.is_valid():

            user = authenticate(
                request=self.request,
                PhoneNumber=data.cleaned_data['phone_number'],
                password=data.cleaned_data['password'],
            )
            if user is not None:
                login(self.request, user)
                messages.success(self.request, "با موفقیت وارد سایت شدید")
            else:
                messages.error(self.request, "اطلاعات وارد شده درست نمی باشد")
                return self.request.META["HTTP_REFERER"]

        else:
            messages.error(self.request, data.errors)
            return reverse_lazy("user:auth")

        if next_url := self.request.POST.get("next"):

            if url_has_allowed_host_and_scheme(
                    next_url,
                    allowed_hosts={self.request.get_host()},
                    require_https=self.request.is_secure(),
            ):
                return next_url

        return reverse_lazy("site:main")