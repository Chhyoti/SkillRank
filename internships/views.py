from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import InternshipPostingForm


@login_required
def create_posting(request):
    profile = request.user.profile

    if profile.role != 'EMPLOYER':
        messages.error(request, "Only employers can post internships.")
        return redirect('home')

    if request.method == 'POST':
        form = InternshipPostingForm(request.POST)
        if form.is_valid():
            posting = form.save(commit=False)
            posting.employer = profile
            posting.save()
            form.save_m2m()  # save many-to-many skills
            messages.success(request, f"Posted '{posting.title}' successfully!")
            return redirect('users:employer_dashboard')
    else:
        form = InternshipPostingForm()

    return render(request, 'internships/create_posting.html', {'form': form})

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import InternshipPosting, Application


@login_required
def view_posting_applications(request, pk):
    posting = get_object_or_404(InternshipPosting, pk=pk)

    # Only the employer who created this posting can view its applications
    if posting.employer != request.user.profile:
        messages.error(request, "You do not have permission to view applications for this posting.")
        return redirect('users:employer_dashboard')

    applications = posting.applications.select_related('intern__user').order_by('-applied_at')

    context = {
        'posting': posting,
        'applications': applications,
    }
    return render(request, 'internships/view_posting_applications.html', context)

@login_required
def update_application_status(request, pk):
    application = get_object_or_404(Application, pk=pk, posting__employer=request.user.profile)

    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Application.STATUS_CHOICES):
            application.status = new_status
            application.save()
            messages.success(request, f"Status updated to {application.get_status_display()}.")
        else:
            messages.error(request, "Invalid status selected.")

    # Redirect back to the applications list
    return redirect('internships:view_posting_applications', pk=application.posting.pk)

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Max, Count
from .models import InternshipPosting, Application
from .utils import calculate_match_score, get_ranked_candidates


@login_required
def view_candidates(request):
    profile = request.user.profile
    if profile.role != 'EMPLOYER':
        messages.error(request, "Only employers can view candidates.")
        return redirect('users:home')

    # All active postings by this employer
    my_postings = InternshipPosting.objects.filter(employer=profile, is_active=True)

    if not my_postings.exists():
        messages.info(request, "You have no active postings yet.")
        return redirect('users:employer_dashboard')

    # All applications to any of my postings
    applications = Application.objects.filter(posting__in=my_postings)

    # Unique interns who applied
    interns = set(app.intern for app in applications)

    candidate_list = []

    for intern in interns:
        # All applications by this intern to my postings
        intern_apps = applications.filter(intern=intern)

        # Find highest match score across all their applications
        highest_score = 0
        for app in intern_apps:
            score = calculate_match_score(intern, app.posting)
            if score > highest_score:
                highest_score = score

        candidate_list.append({
            'intern': intern,
            'highest_score': highest_score,
            'application_count': intern_apps.count(),
            'highest_status': intern_apps.aggregate(highest=Max('status'))['highest'] or 'PENDING',
        })

    # Sort by highest score descending
    candidate_list.sort(key=lambda x: x['highest_score'], reverse=True)

    context = {
        'candidates': candidate_list,
        'total_candidates': len(candidate_list),
    }
    return render(request, 'internships/view_candidates.html', context)


# manage application view 
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count
from .models import Application


@login_required
def manage_all_applications(request):
    profile = request.user.profile
    if profile.role != 'EMPLOYER':
        messages.error(request, "Only employers can manage applications.")
        return redirect('users:home')

    # All applications to any of this employer's postings
    applications = Application.objects.filter(
        posting__employer=profile
    ).select_related('intern__user', 'posting').order_by('-applied_at')

    # Optional: group by posting for display
    postings_with_counts = profile.postings.annotate(
        app_count=Count('applications')
    ).filter(app_count__gt=0)

    context = {
        'applications': applications,
        'total_applications': applications.count(),
        'postings_with_counts': postings_with_counts,
    }
    return render(request, 'internships/manage_all_applications.html', context)


@login_required
def update_application_status(request, application_id):
    application = get_object_or_404(Application, pk=application_id, posting__employer=request.user.profile)

    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Application.STATUS_CHOICES):
            application.status = new_status
            application.save()
            messages.success(request, f"Application status updated to {application.get_status_display()}.")
        else:
            messages.error(request, "Invalid status.")

    # Redirect back to global manage page
    return redirect('internships:manage_all_applications')

# top matched 

@login_required
def view_top_matches(request):
    """
    Shows only the top 10 highest-ranked interns (preview / focused view).
    Used when clicking "View Top Matches" from the dashboard card.
    """
    profile = request.user.profile
    if profile.role != 'EMPLOYER':
        messages.error(request, "Only employers can view top matches.")
        return redirect('users:home')

    # Get only top 10
    top_matches = get_ranked_candidates(profile, limit=10)

    context = {
        'top_matches': top_matches,
        'total_top_matches': len(top_matches),
    }
    return render(request, 'internships/view_top_matches.html', context)