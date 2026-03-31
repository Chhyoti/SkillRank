from pyexpat.errors import messages
from urllib import request
from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import FormView
from django.urls import reverse_lazy
from .forms import ProfileForm, UserRegisterForm
from django.http import HttpResponseRedirect
from django.db.models import Count

def home(request):
    return render(request, 'users/home.html')

class RegisterView(FormView):
    template_name = 'users/register.html'
    form_class = UserRegisterForm
    success_url = reverse_lazy('users:login')

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

class CustomLoginView(LoginView):
    template_name = 'users/login.html'

    def post(self, request, *args, **kwargs):
        print("\n=== POST to /login/ received ===")
        print("POST data:", request.POST)
        print("Current user before auth:", request.user)
        response = super().post(request, *args, **kwargs)
        print("Response after super().post:", response.status_code, response.url if hasattr(response, 'url') else "No url")
        return response

    def get_success_url(self):
        print("\n=== get_success_url called ===")
        print("Authenticated user:", self.request.user.username if self.request.user.is_authenticated else "Anonymous")
        print("Has profile?", hasattr(self.request.user, 'profile'))
        if hasattr(self.request.user, 'profile'):
            print("Role:", self.request.user.profile.role)
        else:
            print("WARNING: No profile attribute!")

        # Force a visible redirect for testing
        return '/intern/dashboard/'  # ← temporary hardcode to test if redirect works at all

class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('users:home')

@login_required
def employer_dashboard(request):
    if request.user.profile.role != 'EMPLOYER':
        return redirect('users:intern_dashboard') 
    postings = request.user.profile.postings.filter(is_active=True).annotate(application_count=Count('applications')).order_by('-created_at')

    context = {
        'postings': postings
    }
    return render(request, 'users/employer_dashboard.html', context)

@login_required
def intern_dashboard(request):
    if request.user.profile.role != 'INTERN':
        return redirect('users:employer_dashboard')
    return render(request, 'users/intern_dashboard.html')
    


from django.contrib.auth.mixins import AccessMixin

class EmployerRequiredMixin(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.profile.role != 'EMPLOYER':
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)
    

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Profile


@login_required
def view_intern_profile(request, profile_id):
    intern_profile = get_object_or_404(Profile, pk=profile_id, role='INTERN')

    # Optional: security - only employers can view intern profiles
    if request.user.profile.role != 'EMPLOYER':
        messages.error(request, "Only employers can view intern profiles.")
        return redirect('users:home')

    context = {
        'intern_profile': intern_profile,
        'skills': intern_profile.skills.all().order_by('skill__name'),
    }
    return render(request, 'users/view_intern_profile.html', context)


# top employees
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from internships.utils import get_ranked_candidates, get_top_matches


@login_required
def employer_dashboard(request):
    if request.user.profile.role != 'EMPLOYER':
        return redirect('users:intern_dashboard')

    # Postings with application count
    postings = request.user.profile.postings.filter(
        is_active=True
    ).annotate(
        application_count=Count('applications')
    ).order_by('-created_at')

    # Top 5 ranked matches for the card preview
    top_matches = get_ranked_candidates(request.user.profile, limit=5)
    context = {
        'postings': postings,
        'top_matches': top_matches,
    }

    return render(request, 'users/employer_dashboard.html', context)

# view for editing profile (intern side)
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
from .forms import ProfileForm  # your form name


@login_required
def edit_intern_profile(request):
    if request.user.profile.role != 'INTERN':
        messages.error(request, "Only interns can edit this profile.")
        return redirect('users:intern_dashboard')

    profile = request.user.profile

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully! Your CV has been saved.")
            return redirect('users:intern_dashboard')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ProfileForm(instance=profile)

    context = {
        'form': form,
        'profile': profile,  # to show current CV link
        'title': 'Update Your Profile',
    }
    return render(request, 'users/edit_intern_profile.html', context)


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
        'page_title': 'Top Matches',
    }
    return render(request, 'users/top_matches.html', context)

# employer side top matched candidates views
@login_required
def employer_top_matches(request):
    if request.user.profile.role != 'EMPLOYER':
        messages.error(request, "This page is for employers only.")
        return redirect('users:employer_dashboard')

    top_candidates = get_ranked_candidates(request.user.profile, limit=15)

    # Filter only candidates with 50% or higher
    top_candidates = [c for c in top_candidates if c.get('highest_score', 0) >= 50]

    context = {
        'top_candidates': top_candidates,
    }
    return render(request, 'internships/view_top_matches.html', context)