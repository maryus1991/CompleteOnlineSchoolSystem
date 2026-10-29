from django.contrib import messages
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView
from apps.ticket.models import Ticket, TicketChat
from apps.users.advisers.forms.ticket import TicketCreateForm
from apps.users.advisers.mixins import AdviserMixin


class TicketListView(AdviserMixin, ListView):
    """adviser and adviser student ticket list """
    model = Ticket
    template_name = "adviser/tickets/list.html"
    context_object_name = "tickets"
    paginate_by = 100

    def get_queryset(self):
        student_user_ids = self.get_adviser_students_queryset().values_list("user_id", flat=True)
        return (
            Ticket.objects.filter(
                Q(user=self.request.user) | Q(user_id__in=student_user_ids)
            )
            .select_related("user")
            .annotate(chats_count=Count("chats"))
            .order_by("-pk")
        )


class TicketCreateView(AdviserMixin, CreateView):
    """ticket creation view"""
    model = Ticket
    form_class = TicketCreateForm
    template_name = "adviser/tickets/create.html"
    success_url = reverse_lazy("adviser:ticket-list")

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.status = Ticket.TicketStatus.awating_admin
        messages.success(self.request, "تیکت شما ارسال شد و در دست بررسی است.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, form.errors)
        return super().form_invalid(form)


class TicketChatView(AdviserMixin, DetailView):
    """ticket message sent """
    model = Ticket
    template_name = "adviser/tickets/detail.html"
    context_object_name = "ticket"

    def get_queryset(self):
        student_user_ids = self.get_adviser_students_queryset().values_list("user_id", flat=True)
        return (
            Ticket.objects.filter(
                Q(user=self.request.user) | Q(user_id__in=student_user_ids)
            )
            .select_related("user")
            .prefetch_related("chats")
        )

    def get_object(self, *args, **kwargs):
        obj = get_object_or_404(self.get_queryset(), pk=self.kwargs.get("pk"))
        if obj.user_id == self.request.user.id:
            obj.chats.update(is_read_by_user=True)
        else:
            obj.chats.update(is_read_by_admin=True)
        return obj

    def post(self, request, pk):
        ticket = get_object_or_404(self.get_queryset(), pk=pk)
        message = request.POST.get("message", "").strip()
        if message:
            if ticket.user_id == request.user.id:
                TicketChat.objects.create(
                    ticket=ticket,
                    user_message=message,
                    is_read_by_admin=False,
                    is_read_by_user=True,
                )
                ticket.status = Ticket.TicketStatus.awating_admin
            else:
                TicketChat.objects.create(
                    ticket=ticket,
                    admin=request.user,
                    admin_message=message,
                    is_read_by_admin=True,
                    is_read_by_user=False,
                )
                ticket.status = Ticket.TicketStatus.awating_user
            ticket.save(update_fields=["status"])
            messages.success(request, "پاسخ شما ثبت شد.")
        return redirect("adviser:ticket-chat", pk=ticket.pk)
