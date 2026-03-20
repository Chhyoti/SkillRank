from django import forms
from .models import InternshipPosting


class InternshipPostingForm(forms.ModelForm):
    class Meta:
        model = InternshipPosting
        fields = ['title', 'description', 'location', 'duration_months', 'required_skills']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
            'required_skills': forms.CheckboxSelectMultiple(),
        }