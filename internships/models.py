from django.db import models

# Create your models here.
from django.db import models
from django.conf import settings
from skills.models import Skill


class InternshipPosting(models.Model):
    employer = models.ForeignKey(
        'users.Profile',
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'EMPLOYER'},
        related_name='postings'
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=150, blank=True)
    duration_months = models.PositiveSmallIntegerField(default=3)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    required_skills = models.ManyToManyField(Skill, related_name='required_in_postings', blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} by {self.employer.user.username}"


class Application(models.Model):
    STATUS_CHOICES = [
        ('VIEWED', 'Viewed'),
        ('SHORTLISTED', 'Shortlisted'),
        ('REJECTED', 'Rejected'),
        ('PENDING', 'Pending'),
    ]

    intern = models.ForeignKey(
        'users.Profile',
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'INTERN'},
        related_name='applications'
    )
    posting = models.ForeignKey(InternshipPosting, on_delete=models.CASCADE, related_name='applications')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    applied_at = models.DateTimeField(auto_now_add=True)
    cover_letter = models.TextField(blank=True)

    class Meta:
        unique_together = ('intern', 'posting')  # one application per intern per posting
        ordering = ['-applied_at']

    def __str__(self):
        return f"{self.intern.user.username} → {self.posting.title}"