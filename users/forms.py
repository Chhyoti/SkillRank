from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile


# Registration form (shared for intern + employer)
class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    role = forms.ChoiceField(
        choices=Profile.role.field.choices,  # reads choices from model field
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'role']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
    
        if commit:
            user.save()
        
        # Use get_or_create instead of create
        profile, created = Profile.objects.get_or_create(
            user=user,
            defaults={'role': self.cleaned_data['role']}
        )
        
        # If profile already existed, update role if needed
        if not created:
            profile.role = self.cleaned_data['role']
            profile.save()
    
        return user
    
    


# Profile edit form (for interns – mainly CV upload)
class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['cv']  # add other fields later if needed (bio, location, etc.)

        widgets = {
            'cv': forms.FileInput(attrs={
                'accept': '.pdf,.doc,.docx',
                'class': 'form-control',
            # 'skills':forms.CheckboxSelectMultiple(),
            }),
        }