from django.db import models
from django.contrib.auth.models import User
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


class SurveyResponse(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.organization.name} ({self.created_at.date()})"


class Answer(models.Model):
    RATING_CHOICES = [(i, str(i)) for i in range(1, 11)]
    
    response = models.ForeignKey(SurveyResponse, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(choices=RATING_CHOICES)
    
    class Meta:
        unique_together = ['response', 'question']
    
    def __str__(self):
        return f"{self.question.text[:30]}... - {self.rating}/10"
