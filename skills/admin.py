from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Skill, UserSkill


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'created_at')
    search_fields = ('name', 'category', 'description')
    list_filter = ('category',)
    ordering = ('name',)
    


@admin.register(UserSkill)
class UserSkillAdmin(admin.ModelAdmin):
    list_display = ('profile', 'skill', 'get_proficiency_display', 'added_at')
    list_filter = ('proficiency', 'added_at')
    search_fields = ('profile__user__username', 'skill__name')
    raw_id_fields = ('profile', 'skill')  # better UX with many users/skills