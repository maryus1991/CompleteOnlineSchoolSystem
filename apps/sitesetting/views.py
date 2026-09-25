from django.views.generic import TemplateView, CreateView
from django.contrib import messages
from apps.sitesetting.forms import ContactForm
from django.urls import reverse_lazy

class Main(TemplateView):
    template_name = 'main/index.html'

class Contact(CreateView):
    template_name = 'main/site/contact.html'
    form_class = ContactForm
    success_url = reverse_lazy('site:contact')

    def form_valid(self, form):
        messages.success(self.request, "پیام شما ارسال شد")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.success(self.request, form.errors, fail_silently=True)
        return super().form_invalid(form)