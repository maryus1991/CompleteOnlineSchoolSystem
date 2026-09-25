from typing import Any

from django.http import HttpRequest, HttpResponseBase
from django.shortcuts import redirect
from django.views.generic import TemplateView, CreateView, ListView
from django.contrib import messages
from apps.sitesetting.forms import ContactForm, CounselingForm
from django.urls import reverse_lazy

from apps.sitesetting.models import FAQ, TimeLine, TestMonomials



class Main(TemplateView):
    template_name = 'main/index.html'

class About(TemplateView):
    template_name = 'main/site/about.html'

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponseBase:
        if not request.site.about_active:
            messages.error(request, "این صفحه غیر فعال میباشد")
            return redirect("site:main")
        return super().dispatch(request, *args, **kwargs)


    def get_context_data(self, **kwargs: Any) -> dict:
        data = super().get_context_data(**kwargs)

        data.update(
            {
                "timeline": TimeLine.objects.filter(is_active=True).all(),
                "testimonials": TestMonomials.objects.filter(is_active=True).all(),
            }
        )

        return data

class FAQListView(ListView):
    """for list faqs"""

    template_name = 'main/site/faq.html'
    queryset = FAQ.objects.filter(is_active=True).all()
    context_object_name = 'items'

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponseBase:
        if not request.site.faq_active:
            messages.error(request, "این صفحه غیر فعال میباشد")
            return redirect("site:main")
        return super().dispatch(request, *args, **kwargs)

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
    success_url = reverse_lazy('site:counseling')

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