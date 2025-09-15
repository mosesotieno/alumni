from django.db import models
from django.core.validators import MinValueValidator
from django.urls import reverse

class Alumnus(models.Model):
    full_name = models.CharField(max_length=100)
    contact = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    
    class Meta:
        verbose_name_plural = "alumni"
    
    def __str__(self):
        return self.full_name
    
    def get_absolute_url(self):
        return reverse('alumnus-detail', kwargs={'pk': self.pk})

class Event(models.Model):
    name = models.CharField(max_length=100)
    date = models.DateField(blank=True, null=True)
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('event-detail', kwargs={'pk': self.pk})

class Contribution(models.Model):
    alumnus = models.ForeignKey(Alumnus, on_delete=models.CASCADE, related_name='contributions')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='contributions')
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    notes = models.CharField(max_length=200, blank=True)
    
    class Meta:
        unique_together = ['alumnus', 'event']  # Prevent duplicate contributions
    
    def __str__(self):
        return f"{self.alumnus} - {self.event}: Ksh {self.amount}"
    
    def get_absolute_url(self):
        return reverse('contribution-detail', kwargs={'pk': self.pk})