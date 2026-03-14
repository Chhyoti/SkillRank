from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import InternshipPosting, Application


@admin.register(InternshipPosting)
class InternshipPostingAdmin(admin.ModelAdmin):
    list_display = ('title', 'employer', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('title', 'description', 'employer__user__username')
    filter_horizontal = ('required_skills',)  #  widget for many-to-many


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('intern', 'posting', 'status', 'applied_at')
    list_filter = ('status', 'applied_at')
    search_fields = ('intern__user__username', 'posting__title')
    raw_id_fields = []
    