from django.contrib import admin
from .models import Alumnus, Event, Contribution

@admin.register(Alumnus)
class AlumnusAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'contact', 'email']
    search_fields = ['full_name', 'contact', 'email']

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['name', 'date']
    search_fields = ['name']

@admin.register(Contribution)
class ContributionAdmin(admin.ModelAdmin):
    list_display = ['alumnus', 'event', 'amount', 'notes']
    list_filter = ['event', 'alumnus']
    search_fields = ['alumnus__full_name', 'event__name']