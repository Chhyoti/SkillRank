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


@login_required
def view_posting_applications(request, pk):
    # Get the posting — only if it belongs to the current employer
    posting = get_object_or_404(
        InternshipPosting,
        pk=pk,
        employer=request.user.profile,
        is_active=True
    )

    # Get all applications for this posting
    applications = Application.objects.filter(posting=posting).select_related(
        'intern__user'
    ).order_by('-applied_at')

    context = {
        'posting': posting,
        'applications': applications,
        'title': f'Applications for {posting.title}',
    }
    return render(request, 'internships/view_posting_applications.html', context)

# interns browsing view
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import InternshipPosting, Application


@login_required
def browse_postings(request):
    if request.user.profile.role != 'INTERN':
        messages.error(request, "Only interns can browse internships.")
        return redirect('users:home')

    # All currently active postings
    postings = InternshipPosting.objects.filter(
        is_active=True
    ).select_related(
        'employer__user'
    ).prefetch_related(
        'required_skills'
    ).order_by('-created_at')

    # IDs of postings this intern has already applied to
    applied_posting_ids = set(
        Application.objects.filter(
            intern=request.user.profile
        ).values_list('posting_id', flat=True)
    )

    context = {
        'postings': postings,
        'applied_posting_ids': applied_posting_ids,
        'page_title': 'Browse Internships',
    }
    return render(request, 'internships/browse_postings.html', context)

# apply internship view
@login_required
def apply_to_posting(request, posting_id):
    if request.user.profile.role != 'INTERN':
        messages.error(request, "Only interns can apply to internships.")
        return redirect('users:home')

    posting = get_object_or_404(InternshipPosting, pk=posting_id, is_active=True)

    # Check if already applied
    if Application.objects.filter(intern=request.user.profile, posting=posting).exists():
        messages.info(request, "You have already applied to this internship.")
        return redirect('internships:browse_postings')

    if request.method == 'POST':
        cover_letter = request.POST.get('cover_letter', '').strip()

        Application.objects.create(
            intern=request.user.profile,
            posting=posting,
            cover_letter=cover_letter,
            status='PENDING'
        )

        messages.success(request, "Application submitted successfully!")
        return redirect('internships:browse_postings')

    # GET request – show confirmation form
    context = {
        'posting': posting,
    }
    return render(request, 'internships/apply_confirmation.html', context)