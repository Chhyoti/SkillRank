from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from internships.utils import get_top_matches
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


# top applicant skills view (for employers)

# Top matches score view on internside view
@login_required
def top_matches(request):
    if request.user.profile.role != 'INTERN':
        messages.error(request, "This page is for interns only.")
        return redirect('users:home')

    # Reuse of  the same logic 
    top_matches = get_top_matches(request.user.profile, limit=12, min_score=50.0)  

    context = {
        'top_matches': top_matches,
        # 'page_title': 'Top Matches',
    }
    return render(request, 'users/top_matches.html', context)