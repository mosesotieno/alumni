from django import forms
from .models import Alumnus, Event, Contribution

class AlumnusForm(forms.ModelForm):
    class Meta:
        model = Alumnus
        fields = ['full_name', 'contact', 'email']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'contact': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['name', 'date']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

class ContributionForm(forms.ModelForm):
    class Meta:
        model = Contribution
        fields = ['alumnus', 'event', 'amount', 'notes']
        widgets = {
            'alumnus': forms.Select(attrs={'class': 'form-control'}),
            'event': forms.Select(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'notes': forms.TextInput(attrs={'class': 'form-control'}),
        }


class ExportSelectionForm(forms.Form):
    EXPORT_CHOICES = [
        ('all', 'All Events'),
        ('specific', 'Specific Event')
    ]
    
    export_type = forms.ChoiceField(
        choices=EXPORT_CHOICES,
        widget=forms.RadioSelect,
        initial='all'
    )
    
    event = forms.ModelChoiceField(
        queryset=Event.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label="Select an event (if specific)"
    )
