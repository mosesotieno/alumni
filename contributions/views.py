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
from django.http import HttpResponse
from django.http import HttpResponse
from django.template.loader import get_template
from django.db.models import Sum
import pandas as pd
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
import datetime
from .forms import ExportSelectionForm


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


def export_contributions_excel(request):
    """Export all contributions to Excel"""
    # Get all contributions with related data
    contributions = Contribution.objects.select_related('alumnus', 'event').all()
    
    # Create DataFrame
    data = []
    for contrib in contributions:
        data.append({
            'Alumnus Name': contrib.alumnus.full_name,
            'Contact': contrib.alumnus.contact or '',
            'Email': contrib.alumnus.email or '',
            'Event': contrib.event.name,
            'Event Date': contrib.event.date.strftime('%Y-%m-%d') if contrib.event.date else '',
            'Amount (Ksh)': float(contrib.amount),
            'Notes': contrib.notes or '',
            'Entry Date': contrib.id  # Using ID as sequence indicator
        })
    
    df = pd.DataFrame(data)
    
    # Create Excel response
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="chianda_contributions_{}.xlsx"'.format(
        datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    )
    
    # Write to Excel
    with pd.ExcelWriter(response, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Contributions', index=False)
        
        # Add summary sheet
        summary_data = []
        events = Event.objects.annotate(total_amount=Sum('contributions__amount'))
        for event in events:
            summary_data.append({
                'Event': event.name,
                'Date': event.date.strftime('%Y-%m-%d') if event.date else '',
                'Total Contributions': event.contributions.count(),
                'Total Amount (Ksh)': float(event.total_amount or 0)
            })
        
        # Add overall total
        overall_total = Contribution.objects.aggregate(total=Sum('amount'))['total'] or 0
        summary_data.append({
            'Event': 'GRAND TOTAL',
            'Date': '',
            'Total Contributions': Contribution.objects.count(),
            'Total Amount (Ksh)': float(overall_total)
        })
        
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
    
    return response

def export_contributions_pdf(request):
    """Export contributions to PDF"""
    contributions = Contribution.objects.select_related('alumnus', 'event').all()
    
    # Create PDF response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="chianda_contributions_report_{}.pdf"'.format(
        datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    )
    
    # Create PDF document
    doc = SimpleDocTemplate(response, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30,
        alignment=1  # center
    )
    title = Paragraph("Chianda High School - Contributions Report", title_style)
    elements.append(title)
    
    # Date
    date_text = "Generated on: {}".format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M'))
    date_para = Paragraph(date_text, styles['Normal'])
    elements.append(date_para)
    elements.append(Spacer(1, 20))
    
    # Summary Table
    summary_data = [['Event', 'Date', 'Contributions', 'Total Amount (Ksh)']]
    events = Event.objects.annotate(total_amount=Sum('contributions__amount'))
    
    for event in events:
        summary_data.append([
            event.name,
            event.date.strftime('%Y-%m-%d') if event.date else 'N/A',
            str(event.contributions.count()),
            '{:,.2f}'.format(float(event.total_amount or 0))
        ])
    
    # Add grand total
    overall_total = Contribution.objects.aggregate(total=Sum('amount'))['total'] or 0
    summary_data.append([
        'GRAND TOTAL',
        '',
        str(Contribution.objects.count()),
        '{:,.2f}'.format(float(overall_total))
    ])
    
    summary_table = Table(summary_data)
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a472a')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#d4af37')),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(summary_table)
    elements.append(Spacer(1, 30))
    
    # Detailed Contributions
    details_title = Paragraph("Detailed Contributions", styles['Heading2'])
    elements.append(details_title)
    elements.append(Spacer(1, 10))
    
    details_data = [['Alumnus', 'Contact', 'Event', 'Amount (Ksh)', 'Notes']]
    for contrib in contributions:
        details_data.append([
            contrib.alumnus.full_name,
            contrib.alumnus.contact or '',
            contrib.event.name,
            '{:,.2f}'.format(float(contrib.amount)),
            contrib.notes or ''
        ])
    
    details_table = Table(details_data)
    details_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a472a')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (3, 1), (3, -1), 'RIGHT'),  # Right align amounts
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
    ]))
    
    elements.append(details_table)
    
    # Build PDF
    doc.build(elements)
    return response

def export_event_excel(request, event_id):
    """Export contributions for a specific event to Excel"""
    event = get_object_or_404(Event, id=event_id)
    contributions = Contribution.objects.filter(event=event).select_related('alumnus')
    
    # Create DataFrame
    data = []
    for contrib in contributions:
        data.append({
            'Alumnus Name': contrib.alumnus.full_name,
            'Contact': contrib.alumnus.contact or '',
            'Email': contrib.alumnus.email or '',
            'Amount (Ksh)': float(contrib.amount),
            'Notes': contrib.notes or ''
        })
    
    df = pd.DataFrame(data)
    
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="chianda_event_{}_{}.xlsx"'.format(
        event.name.lower().replace(' ', '_'),
        datetime.datetime.now().strftime('%Y%m%d')
    )
    
    with pd.ExcelWriter(response, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name=event.name[:30], index=False)
    
    return response


def export_selection(request):
    """View to select export options"""
    if request.method == 'POST':
        form = ExportSelectionForm(request.POST)
        if form.is_valid():
            export_type = form.cleaned_data['export_type']
            event = form.cleaned_data['event']
            
            if export_type == 'all':
                return export_contributions_excel(request)
            else:
                if event:
                    return export_event_excel(request, event.id)
                else:
                    form.add_error('event', 'Please select an event for specific export')
    else:
        form = ExportSelectionForm()
    
    return render(request, 'contributions/export_selection.html', {'form': form})

def export_pdf_selection(request):
    """View to select PDF export options"""
    if request.method == 'POST':
        form = ExportSelectionForm(request.POST)
        if form.is_valid():
            export_type = form.cleaned_data['export_type']
            event = form.cleaned_data['event']
            
            if export_type == 'all':
                return export_contributions_pdf(request)
            else:
                if event:
                    return export_event_pdf(request, event.id)
                else:
                    form.add_error('event', 'Please select an event for specific export')
    else:
        form = ExportSelectionForm()
    
    return render(request, 'contributions/export_pdf_selection.html', {'form': form})


def export_event_pdf(request, event_id):
    """Export specific event contributions to PDF"""
    event = get_object_or_404(Event, id=event_id)
    contributions = Contribution.objects.filter(event=event).select_related('alumnus')
    
    # Create PDF response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="chianda_event_{}_{}.pdf"'.format(
        event.name.lower().replace(' ', '_'),
        datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    )
    
    # Create PDF document
    doc = SimpleDocTemplate(response, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30,
        alignment=1  # center
    )
    title = Paragraph("Chianda High School - Event Contributions Report", title_style)
    elements.append(title)
    
    # Event Details
    event_details = [
        ["Event:", event.name],
        ["Date:", event.date.strftime('%Y-%m-%d') if event.date else 'Not specified'],
        ["Total Contributions:", str(contributions.count())],
        ["Total Amount:", "Ksh {:,.2f}".format(float(
            contributions.aggregate(total=Sum('amount'))['total'] or 0
        ))]
    ]
    
    event_table = Table(event_details)
    event_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#1a472a')),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.whitesmoke),
        ('BACKGROUND', (1, 0), (1, -1), colors.HexColor('#f8f9fa')),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
    ]))
    
    elements.append(event_table)
    elements.append(Spacer(1, 30))
    
    # Date
    date_text = "Generated on: {}".format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M'))
    date_para = Paragraph(date_text, styles['Normal'])
    elements.append(date_para)
    elements.append(Spacer(1, 20))
    
    # Contributions Table
    details_data = [['Alumnus', 'Contact', 'Amount (Ksh)', 'Notes']]
    for contrib in contributions:
        details_data.append([
            contrib.alumnus.full_name,
            contrib.alumnus.contact or '',
            '{:,.2f}'.format(float(contrib.amount)),
            contrib.notes or ''
        ])
    
    # Add total row
    total_amount = contributions.aggregate(total=Sum('amount'))['total'] or 0
    details_data.append([
        'TOTAL',
        '',
        '{:,.2f}'.format(float(total_amount)),
        ''
    ])
    
    details_table = Table(details_data)
    details_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a472a')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (2, 1), (2, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#d4af37')),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('FONTSIZE', (0, 1), (-1, -2), 8),
    ]))
    
    elements.append(details_table)
    
    # Build PDF
    doc.build(elements)
    return response