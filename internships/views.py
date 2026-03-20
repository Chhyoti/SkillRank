from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Max
from .models import InternshipPosting, Application
from .forms import InternshipPostingForm  # assume you have this


# Helper function (keep or move to utils.py)
def calculate_match_score(intern_profile, posting):
    required = posting.required_skills.all()
    if not required.exists():
        return 0.0

    intern_skills = {us.skill: us.proficiency for us in intern_profile.skills.all()}

    total_weight = 0.0
    for req_skill in required:
        if req_skill in intern_skills:
            total_weight += intern_skills[req_skill] / 5.0

    score = (total_weight / required.count()) * 100
    return round(score, 1)


@login_required
def create_posting(request):
    if request.user.profile.role != 'EMPLOYER':
        messages.error(request, "Only employers can create postings.")
        return redirect('users:home')

    if request.method == 'POST':
        form = InternshipPostingForm(request.POST)
        if form.is_valid():
            posting = form.save(commit=False)
            posting.employer = request.user.profile
            posting.save()
            form.save_m2m()  # required_skills
            messages.success(request, "Posting created!")
            return redirect('users:employer_dashboard')
    else:
        form = InternshipPostingForm()

    return render(request, 'internships/create_posting.html', {'form': form})


@login_required
def view_candidates(request):
    profile = request.user.profile
    if profile.role != 'EMPLOYER':
        messages.error(request, "Only employers can view candidates.")
        return redirect('users:home')

    # All applications to this employer's postings
    applications = Application.objects.filter(
        posting__employer=profile
    ).select_related('intern__user', 'posting').order_by('-applied_at')

    # Group by intern for ranking
    from collections import defaultdict
    intern_apps = defaultdict(list)
    for app in applications:
        intern_apps[app.intern].append(app)

    # Build ranked list
    candidates = []
    for intern, apps in intern_apps.items():
        highest_score = max(
            calculate_match_score(intern, app.posting) for app in apps
        )
        candidates.append({
            'intern': intern,
            'highest_score': highest_score,
            'application_count': len(apps),
            'highest_status': max(app.status for app in apps) if apps else 'PENDING',
            'applications': apps,  # for status change
        })

    # Sort
    candidates.sort(key=lambda x: (-x['highest_score'], -x['application_count'], x['intern'].user.username.lower()))

    context = {
        'candidates': candidates,
        'total_candidates': len(candidates),
    }
    return render(request, 'internships/view_candidates.html', context)


@login_required
def update_application_status(request, application_id):
    application = get_object_or_404(
        Application,
        pk=application_id,
        posting__employer=request.user.profile
    )

    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Application.STATUS_CHOICES):
            application.status = new_status
            application.save()
            messages.success(request, f"Status updated to {application.get_status_display()}.")
        else:
            messages.error(request, "Invalid status.")

    return redirect('internships:view_candidates')