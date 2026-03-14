from django import forms
from .models import Skill, UserSkill


class AddSkillForm(forms.ModelForm):
    class Meta:
        model = UserSkill
        fields = ['skill', 'proficiency']
        widgets = {
            'skill': forms.Select(attrs={'class': 'form-select'}),
            'proficiency': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, profile, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Exclude already added skills
        used_skills = profile.skills.values_list('skill_id', flat=True)
        self.fields['skill'].queryset = Skill.objects.exclude(id__in=used_skills)