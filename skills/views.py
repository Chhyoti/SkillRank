from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import UserSkill, Skill
from .forms import AddSkillForm


@login_required
def add_skill(request):
    profile = request.user.profile

    if profile.role != 'INTERN':
        messages.error(request, "Only interns can add skills.")
        return redirect('users:intern_dashboard')

    if request.method == 'POST':
        form = AddSkillForm(profile, request.POST)
        if form.is_valid():
            user_skill = form.save(commit=False)
            user_skill.profile = profile
            user_skill.save()
            messages.success(request, f"Added {user_skill.skill.name} ({user_skill.get_proficiency_display()})")
            return redirect('users:intern_dashboard')
    else:
        form = AddSkillForm(profile)

    return render(request, 'skills/add_skill.html', {'form': form})


@login_required
def remove_skill(request, pk):
    user_skill = get_object_or_404(UserSkill, pk=pk, profile=request.user.profile)
    skill_name = user_skill.skill.name
    user_skill.delete()
    messages.success(request, f"Removed {skill_name}")
    return redirect('users:intern_dashboard')