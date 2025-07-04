from django.db import models
from django.contrib.auth.models import User


class Organization(models.Model):
    name = models.CharField(max_length=200)
    questions_per_cycle = models.PositiveIntegerField(default=5, help_text="Number of questions to ask in each survey cycle")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


class OrganizationMembership(models.Model):
    ROLE_CHOICES = [
        ('owner', 'Owner'),
        ('admin', 'Admin'),
        ('member', 'Member'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
    title = models.CharField(max_length=100, blank=True, help_text="Job title or position")
    reports_to = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='direct_reports')
    joined_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'organization']
    
    def __str__(self):
        return f"{self.user.email} - {self.organization.name} ({self.role})"
    
    def get_all_subordinates(self):
        """Get all subordinates (direct and indirect reports)"""
        subordinates = []
        for direct_report in self.direct_reports.all():
            subordinates.append(direct_report)
            subordinates.extend(direct_report.get_all_subordinates())
        return subordinates
