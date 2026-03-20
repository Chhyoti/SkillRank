from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    ROLE_CHOICES = (
        ('EMPLOYER', 'Employer'),
        ('INTERN', 'Intern'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    # skills = models.ManyToManyField('skills.skill',through='skills.UserSkill',related_name='profiles')
    # updated_at = models.DateTimeField(auto_now=True)
    # ... other fields like full_name, cv, etc. ...

    def __str__(self):
        return f"{self.user.username} ({self.role})"


    @property
    def is_intern(self):
        return self.role == 'INTERN'

    @property
    def is_employer(self):
        return self.role == 'EMPLOYER'
    
# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from django.contrib.auth.models import User
# from .models import Profile

# @receiver(post_save, sender=User)
# def create_user_profile(sender, instance, created, **kwargs):
#     if created:
#         Profile.objects.create(user=instance)

# @receiver(post_save, sender=User)
# def save_user_profile(sender, instance, **kwargs):
#     instance.profile.save()

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=10, choices=[('INTERN', 'Intern'), ('EMPLOYER', 'Employer')])
    
    # Common fields
    # bio = models.TextField(blank=True)
    # location = models.CharField(max_length=100, blank=True)
    
    # NEW: CV field (only relevant for interns)
    cv = models.FileField(
        upload_to='cvs/%Y/%m/%d/',
        null=True,
        blank=True,
        verbose_name="Curriculum Vitae (CV)",
        help_text="Upload your CV/Resume (PDF preferred)"
    )

    def __str__(self):
        return f"{self.user.username} ({self.role})"