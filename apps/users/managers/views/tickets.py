from django.contrib import messages
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.views.generic import ListView, TemplateView

from apps.ticket.models import Ticket, TicketChat
from apps.users.managers.forms.tickets import (
    ManagerTicketAssignForm,
    ManagerTicketReplyForm,
)
from apps.users.managers.mixins import ManagerMixin


class TicketListView(ManagerMixin, ListView):
    template_name = "manager/tickets/ticket_list.html"
    context_object_name = "tickets"
    paginate_by = 20
    permission_field = "can_manage_tickets"

    def get_queryset(self):
        qs = (
            self.get_school_tickets_queryset()
            .annotate(chats_count=Count("chats", distinct=True))
            .order_by("-id")
        )
        q = (self.request.GET.get("q") or "").strip()
        status = (self.request.GET.get("status") or "").strip()
        priority = (self.request.GET.get("priority") or "").strip()
        role = (self.request.GET.get("role") or "").strip()

        if q:
            qs = qs.filter(
                Q(name__icontains=q)
                | Q(description__icontains=q)
                | Q(user__first_name__icontains=q)
                | Q(user__last_name__icontains=q)
                | Q(user__PhoneNumber__icontains=q)
            )
        if status:
            qs = qs.filter(status=status)
        if priority:
            qs = qs.filter(priority=priority)
        if role:
            qs = qs.filter(user__type_of_user=role)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["ticket_statuses"] = Ticket.TicketStatus.choices
        ctx["ticket_priorities"] = Ticket.TicketPriority.choices
        return ctx


class TicketDetailView(ManagerMixin, TemplateView):
    template_name = "manager/tickets/ticket_detail.html"
    permission_field = "can_manage_tickets"

    def get_ticket(self):
        return get_object_or_404(
            self.get_school_tickets_queryset(), pk=self.kwargs["pk"]
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ticket = self.get_ticket()
        ctx["ticket"] = ticket
        ctx["chats"] = ticket.chats.select_related("admin").order_by("id")
        if "reply_form" not in ctx:
            ctx["reply_form"] = ManagerTicketReplyForm(
                initial={"status": Ticket.TicketStatus.awating_user}
            )
        if "assign_form" not in ctx:
            ctx["assign_form"] = ManagerTicketAssignForm(
                instance=ticket, school=self.get_school()
            )
        return ctx

    def post(self, request, *args, **kwargs):
        ticket = self.get_ticket()
        school = self.get_school()
        action = request.POST.get("action", "reply")

        if action == "assign":
            assign_form = ManagerTicketAssignForm(
                request.POST, instance=ticket, school=school
            )
            if assign_form.is_valid():
                updated = assign_form.save(commit=False)
                if not updated.school_id:
                    updated.school = school
                updated.save()
                messages.success(
                    request,
                    "وضعیت و ارجاع تیکت با موفقیت بروزرسانی شد.",
                )
                return redirect("manager:ticket-detail", pk=ticket.pk)
            return self.render_to_response(
                self.get_context_data(assign_form=assign_form)
            )

        reply_form = ManagerTicketReplyForm(request.POST)
        if reply_form.is_valid():
            TicketChat.objects.create(
                ticket=ticket,
                admin=request.user,
                admin_message=reply_form.cleaned_data["admin_message"],
                is_read_by_admin=True,
                is_read_by_user=False,
            )
            new_status = (
                reply_form.cleaned_data.get("status")
                or Ticket.TicketStatus.awating_user
            )
            ticket.status = new_status
            if not ticket.school_id:
                ticket.school = school
            ticket.save(update_fields=["status", "school", "updated_at"])
            messages.success(request, "پاسخ شما در تیکت ثبت شد.")
            return redirect("manager:ticket-detail", pk=ticket.pk)

        return self.render_to_response(self.get_context_data(reply_form=reply_form))


class TicketToggleActiveView(ManagerMixin, View):
    permission_field = "can_manage_tickets"

    def post(self, request, pk, *args, **kwargs):
        ticket = get_object_or_404(self.get_school_tickets_queryset(), pk=pk)
        new_state = self.toggle_object_active(ticket)
        status_label = "فعال" if new_state else "غیرفعال"
        messages.info(
            request,
            f"وضعیت تیکت «{ticket.name}» به «{status_label}» تغییر یافت.",
        )
        return redirect(request.META.get("HTTP_REFERER") or "manager:ticket-list")
