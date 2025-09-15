from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('alumni/', views.AlumnusListView.as_view(), name='alumnus-list'),
    path('events/', views.EventListView.as_view(), name='event-list'),
    path('contributions/', views.ContributionListView.as_view(), name='contribution-list'),
    path('alumni/add/', views.AlumnusCreateView.as_view(), name='alumnus-add'),
    path('events/add/', views.EventCreateView.as_view(), name='event-add'),
    path('contributions/add/', views.ContributionCreateView.as_view(), name='contribution-add'),
    path('export/', views.export_data, name='export-data'),
]