from django import forms
from .models import Organization


class OrganizationForm(forms.ModelForm):
    class Meta:
        model = Organization
        fields = ['name', 'questions_per_cycle']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter organization name'}),
            'questions_per_cycle': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '20'})
        }
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if name:
            name = name.strip()
            if len(name) < 2:
                raise forms.ValidationError('Organization name must be at least 2 characters long.')
        return name
    
    def clean_questions_per_cycle(self):
        questions_per_cycle = self.cleaned_data.get('questions_per_cycle')
        if questions_per_cycle and (questions_per_cycle < 1 or questions_per_cycle > 20):
            raise forms.ValidationError('Questions per cycle must be between 1 and 20.')
        return questions_per_cycle