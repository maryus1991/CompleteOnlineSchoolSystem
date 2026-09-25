from typing import Any

from django.http import HttpRequest, HttpResponseBase
from django.shortcuts import redirect
from django.views.generic import TemplateView, CreateView
from django.contrib import messages
from apps.sitesetting.forms import ContactForm, CounselingForm
from django.urls import reverse_lazy

class Main(TemplateView):
    template_name = 'main/index.html'

class Contact(CreateView):
    template_name = 'main/site/contact.html'
    form_class = ContactForm
    success_url = reverse_lazy('site:contact')

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponseBase:
        if not request.site.active_contact:
            messages.error(request, "این صفحه غیر فعال میباشد")
            return redirect("site:main")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, "پیام شما ارسال شد")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.success(self.request, form.errors, fail_silently=True)
        return super().form_invalid(form)

class Counseling(CreateView):
    template_name = 'main/site/free-counseling.html'
    form_class = CounselingForm
    success_url = reverse_lazy('site:contact')

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponseBase:
        if not request.site.active_counseling:
            messages.error(request, "این صفحه غیر فعال میباشد")
            return redirect("site:main")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, "پیام شما ارسال شد")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.success(self.request, form.errors, fail_silently=True)
        return super().form_invalid(form)