from django.db import models
from organizations.models import Organization


class Survey(models.Model):
    organization = models.OneToOneField(Organization, on_delete=models.CASCADE, related_name='survey')
    title = models.CharField(max_length=200, default='Employee Engagement Survey')
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['organization__name']
    
    def __str__(self):
        return f"{self.organization.name} - {self.title}"


class Theme(models.Model):
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='themes')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order', 'name']
        unique_together = ['survey', 'name']
    
    def __str__(self):
        return f"{self.survey.organization.name} - {self.name}"


class Question(models.Model):
    theme = models.ForeignKey(Theme, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order', 'id']
    
    def __str__(self):
        return f"{self.theme.name} - {self.text[:50]}..."
