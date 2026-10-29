from django.views.generic import ListView, TemplateView, RedirectView
from django.contrib.auth import authenticate, login, logout
from .models import User
from .forms import UserLoginForm, UserRegisterForm
from django.urls import reverse_lazy
from django.utils.http import url_has_allowed_host_and_scheme
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from apps.users.students.models import Student
from apps.users.advisers.models import Adviser


class UserLogoutView(LoginRequiredMixin, RedirectView):
    """for logout view"""
    def get_redirect_url(self):
        logout(self.request)
        messages.success(
            self.request,
            "ما همیشه منتظر حضور گرمتان هستیم",
        )
        return reverse_lazy("site:main")


class UserListView(ListView):
    queryset = User.objects.filter(is_active=True, publish=True)
    context_object_name = "items"
    paginate_by = 100
    template_name = "main/teachers/list.html"

    def dispatch(self, request, *args, **kwargs):
        if not request.site.list_users_active:
            messages.error(request, "این صفحه غیر فعال میباشد")
            return redirect("site:main")
        return super().dispatch(request, *args, **kwargs)


class AuthView(TemplateView):
    """auth view"""
    template_name = "main/auth/auth.html"

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data.update({
            "login_form": UserLoginForm(self.request.POST or None),
            "register_form": UserRegisterForm(self.request.POST or None),
            "next": self.request.GET.get("next"),
        })
        return data


class UserRegisterView(RedirectView):
    """user register view"""
    def get_redirect_url(self, *args, **kwargs):
        request = self.request

        if not request.site.register_active:
            messages.error(request, "ثبت‌نام در حال حاضر غیرفعال می‌باشد")
            return reverse_lazy("user:auth")

        if request.method != "POST":
            messages.error(request, "درخواست ثبت‌نام معتبر نیست")
            return reverse_lazy("user:auth")

        form = UserRegisterForm(request.POST)
        if not form.is_valid():
            messages.error(request, "اطلاعات واردشده معتبر نیست")
            messages.error(request, form.errors)
            return reverse_lazy("user:auth")

        try:
            user = User.objects.create_user(
                PhoneNumber=form.cleaned_data["phone_number"],
                password=form.cleaned_data["password"],
                is_verified=True,
            )
            Student.objects.get_or_create(user=user)
        except IntegrityError:
            messages.error(request, "این شماره تلفن قبلاً ثبت‌نام کرده است")
            return reverse_lazy("user:auth")
        except ValidationError as error:
            messages.error(request, error.message)
            return reverse_lazy("user:auth")

        messages.success(request, "ثبت‌نام با موفقیت انجام شد. اکنون وارد شوید.")

        next_url = request.POST.get("next")
        if next_url and url_has_allowed_host_and_scheme(
            next_url,
            allowed_hosts={request.get_host()},
            require_https=request.is_secure(),
        ):
            return next_url

        return reverse_lazy("user:auth")


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
                return self.request.META.get("HTTP_REFERER", reverse_lazy("user:auth"))
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

        if (
            user.type_of_user == User.TypeOfUser.ADVISER
            or Adviser.objects.filter(user=user, is_active=True).exists()
        ):
            return reverse_lazy("adviser:main")

        return reverse_lazy("site:main")
