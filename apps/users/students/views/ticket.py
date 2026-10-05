from django.contrib import messages
from django.db.models import Count
from django.views.generic import ListView, CreateView, DetailView
from apps.ticket.models import Ticket, TicketChat
from apps.ticket.forms import TicketCreateForm
from apps.users.students.mixins import StudentMixin
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect


class TicketListView(StudentMixin, ListView):
    """list the tickets for a student"""


    model = Ticket
    template_name = "dashboard/ticket/list.html"
    context_object_name = "tickets"

    paginate_by = 100

    def get_queryset(self):
        return (
            Ticket.objects
            .filter(user=self.request.user)
            .annotate(chats_count=Count("chats"))
            .order_by("-pk")
        )


class TicketCreateView(StudentMixin, CreateView):
    """ create a new ticket for the student """

    model = Ticket
    form_class = TicketCreateForm
    template_name = "dashboard/ticket/create.html"
    success_url = reverse_lazy("student:ticket-list")

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.status = Ticket.TicketStatus.awating_admin
        messages.success(self.request, "تیکت شما ارسال شد و در دست برسی است")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, form.errors)
        return super().form_invalid(form)


class TicketChatView(StudentMixin, DetailView):
    """ send message of the student and send it to admin """

    model = Ticket
    template_name = "dashboard/ticket/detail.html"
    context_object_name = "ticket"

    def get_queryset(self):
        obj = Ticket.objects.filter(user=self.request.user).prefetch_related("chats")
        return obj

    def get_object(self, *args, **kwargs) :
        obj = get_object_or_404(self.get_queryset(), pk=self.kwargs.get("pk"))
        obj.chats.update(is_read_by_user=True)
        return obj



    def post(self, request, pk):

        ticket = get_object_or_404(
            Ticket,
            pk=pk,
            user=request.user,
        )

        message = request.POST.get("message", "").strip()

        if message:
            TicketChat.objects.create(
                ticket=ticket,
                user_message=message,
                is_read_by_admin=False,
                is_read_by_user=True,
            )

            ticket.status = Ticket.TicketStatus.awating_admin
            ticket.save(update_fields=["status"])

        return redirect(
            "student:ticket-chat",
            pk=ticket.pk,
        )