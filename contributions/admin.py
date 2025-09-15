from django.contrib import admin
from .models import Alumnus, Event, Contribution

@admin.register(Alumnus)
class AlumnusAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'contact', 'email', 'contribution_count']
    search_fields = ['full_name', 'contact', 'email']
    list_filter = ['contributions__event']
    
    def contribution_count(self, obj):
        return obj.contributions.count()
    contribution_count.short_description = 'Total Contributions'

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['name', 'date', 'total_contributions', 'total_amount']
    search_fields = ['name']
    list_filter = ['date']
    
    def total_contributions(self, obj):
        return obj.contributions.count()
    total_contributions.short_description = 'Number of Contributions'
    
    def total_amount(self, obj):
        total = obj.contributions.aggregate(total=Sum('amount'))['total']
        return f"Ksh {total or 0}"
    total_amount.short_description = 'Total Amount'

@admin.register(Contribution)
class ContributionAdmin(admin.ModelAdmin):
    list_display = ['alumnus', 'event', 'amount', 'notes', 'contribution_date']
    list_filter = ['event', 'alumnus']
    search_fields = ['alumnus__full_name', 'event__name', 'notes']
    date_hierarchy = 'id'  # Shows date-based navigation
    
    def contribution_date(self, obj):
        return obj.id  # This will show the order of contributions
    contribution_date.short_description = 'Entry Date'