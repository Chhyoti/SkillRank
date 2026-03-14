from django.db import models

# Create your models here.
from django.db import models
from django.conf import settings


class Skill(models.Model):
    """
    Global/master list of skills.
    Managed by admins or via simple form later.
    """
    name = models.CharField(max_length=120, unique=True)
    category = models.CharField(max_length=80, blank=True, help_text="e.g. Programming, Design, Marketing")
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = "Skills"

    def __str__(self):
        return self.name


class UserSkill(models.Model):
    """
    Junction table: connects Profile ↔ Skill with proficiency level.
    Only interns have skills.
    """
    PROFICIENCY_CHOICES = [
        (1, 'Beginner'),
        (2, 'Elementary'),
        (3, 'Intermediate'),
        (4, 'Advanced'),
        (5, 'Expert'),
    ]

    profile = models.ForeignKey(
        'users.Profile',
        on_delete=models.CASCADE,
        related_name='skills',
        limit_choices_to={'role': 'INTERN'}  # only interns
    )
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    proficiency = models.PositiveSmallIntegerField(choices=PROFICIENCY_CHOICES, default=3)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('profile', 'skill')  # one skill only once per profile
        ordering = ['skill__name']

    def __str__(self):
        return f"{self.profile.user.username} – {self.skill.name} ({self.get_proficiency_display()})"