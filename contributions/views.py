from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Sum, Count
from django.http import JsonResponse
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from .models import Alumnus, Event, Contribution
from .forms import AlumnusForm, EventForm, ContributionForm
from django.contrib import messages
from .models import Alumnus, Event, Contribution
from .forms import AlumnusForm, EventForm, ContributionForm
from django.urls import reverse_lazy


def index(request):
    """Dashboard view"""
    total_alumni = Alumnus.objects.count()
    total_events = Event.objects.count()
    total_contributions = Contribution.objects.count()
    total_amount = Contribution.objects.aggregate(total=Sum('amount'))['total'] or 0
    
    # Event-wise totals
    event_totals = Event.objects.annotate(
        total_amount=Sum('contributions__amount')
    ).values('name', 'total_amount')
    
    # Recent contributions
    recent_contributions = Contribution.objects.select_related('alumnus', 'event')[:10]
    
    context = {
        'total_alumni': total_alumni,
        'total_events': total_events,
        'total_contributions': total_contributions,
        'total_amount': total_amount,
        'event_totals': event_totals,
        'recent_contributions': recent_contributions,
    }
    return render(request, 'contributions/index.html', context)

class AlumnusListView(ListView):
    model = Alumnus
    template_name = 'contributions/alumnus_list.html'
    context_object_name = 'alumni'

class EventListView(ListView):
    model = Event
    template_name = 'contributions/event_list.html'
    context_object_name = 'events'

class ContributionListView(ListView):
    model = Contribution
    template_name = 'contributions/contribution_list.html'
    context_object_name = 'contributions'
    
    def get_queryset(self):
        return Contribution.objects.select_related('alumnus', 'event')

class AlumnusCreateView(CreateView):
    model = Alumnus
    form_class = AlumnusForm
    template_name = 'contributions/alumnus_form.html'
    success_url = '/alumni/'

class EventCreateView(CreateView):
    model = Event
    form_class = EventForm
    template_name = 'contributions/event_form.html'
    success_url = '/events/'

class ContributionCreateView(CreateView):
    model = Contribution
    form_class = ContributionForm
    template_name = 'contributions/contribution_form.html'
    success_url = '/contributions/'

class AlumnusCreateView(CreateView):
    model = Alumnus
    form_class = AlumnusForm
    template_name = 'contributions/alumnus_form.html'
    success_url = reverse_lazy('alumnus-list')
    
    
    def form_valid(self, form):
        messages.success(self.request, 'Alumnus added successfully!')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add Alumnus'
        return context

class EventCreateView(CreateView):
    model = Event
    form_class = EventForm
    template_name = 'contributions/event_form.html'
    success_url = '/events/'
    
    def form_valid(self, form):
        messages.success(self.request, 'Event added successfully!')
        return super().form_valid(form)
    
    
        

class ContributionCreateView(CreateView):
    model = Contribution
    form_class = ContributionForm
    template_name = 'contributions/contribution_form.html'
    success_url = '/contributions/'
    
    def form_valid(self, form):
        messages.success(self.request, 'Contribution recorded successfully!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Error recording contribution. Please check the form.')
        return super().form_invalid(form)

def export_data(request):
    """Export data to JSON (can be extended to CSV/Excel)"""
    data = {
        'alumni': list(Alumnus.objects.values()),
        'events': list(Event.objects.values()),
        'contributions': list(Contribution.objects.values('alumnus__full_name', 'event__name', 'amount', 'notes')),
    }
    return JsonResponse(data)