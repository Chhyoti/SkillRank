def calculate_match_score(intern_profile, posting):
    """
    Returns match percentage (0–100) between intern's skills and posting's required skills.
    Uses proficiency (1–5) to weight each matching skill.
    """
    required = posting.required_skills.all()
    if not required.exists():
        return 0.0

    # Intern's skills as dict {skill: proficiency}
    intern_skills = {us.skill: us.proficiency for us in intern_profile.skills.all()}

    total_weight = 0.0
    for req_skill in required:
        if req_skill in intern_skills:
            # Proficiency 1–5 → 0.2 to 1.0 contribution per skill
            total_weight += intern_skills[req_skill] / 5.0

    # Normalize to percentage
    score = (total_weight / required.count()) * 100
    return round(score, 1)

from django.db.models import Max, Count

from internships.models import Application

# def get_ranked_candidates(employer_profile, limit=None):
#     my_postings = employer_profile.postings.filter(is_active=True)

#     if not my_postings.exists():
#         return []

#     applications = Application.objects.filter(posting__in=my_postings).select_related('intern', 'posting')

#     interns = set(app.intern for app in applications)

#     candidate_list = []

#     for intern in interns:
#         intern_apps = applications.filter(intern=intern)

#         highest_score = 0
#         for app in intern_apps:
#             score = calculate_match_score(intern, app.posting)
#             if score > highest_score:
#                 highest_score = score

#         candidate_list.append({
#             'intern': intern,
#             'highest_score': highest_score,
#             'application_count': intern_apps.count(),
#             'highest_status': intern_apps.aggregate(highest=Max('status'))['highest'] or 'PENDING',
#         })

    
#     candidate_list.sort(
#     key=lambda x: (
#         -x['highest_score'],               # Primary: higher score first (negative for descending)
#         -x['application_count'],           # Secondary: more applications first
#         x['intern'].user.username.lower()  # Tertiary: alphabetical by username (case-insensitive)
#     )
# )

#     if limit is not None:
#         candidate_list = candidate_list[:limit]

#     return candidate_list 
def get_ranked_candidates(employer_profile, limit=None):
    """
    Simple and reliable version to get top ranked candidates for employer.
    """
    # Get all active postings of this employer
    my_postings = employer_profile.postings.filter(is_active=True)
    if not my_postings.exists():
        return []

    # Get all applications for these postings
    applications = Application.objects.filter(posting__in=my_postings)\
        .select_related('intern__user', 'posting')

    if not applications.exists():
        return []

    # Group by intern
    from collections import defaultdict
    intern_data = defaultdict(list)

    for app in applications:
        intern_data[app.intern].append(app)

    candidate_list = []

    for intern, intern_apps in intern_data.items():
        highest_score = 0.0
        best_posting_title = "Multiple postings"
        best_app = intern_apps[0]  # default to first app for title if only one

        for app in intern_apps:
            score = calculate_match_score(intern, app.posting)
            if score > highest_score:
                highest_score = score
                best_posting_title = app.posting.title 
                best_app = app  # Keep the application with highest score

        candidate_list.append({
            'intern': intern,
            'highest_score': highest_score,
            'total_applications': len(intern_apps),
            'best_posting_title': best_posting_title,
            'application': best_app,  # Include the best application for status and other details
        })

    # Sort by highest score first
    candidate_list.sort(key=lambda x: -x['highest_score'])

    if limit is not None:
        candidate_list = candidate_list[:limit]

    return candidate_list

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

# Top match score of the internships on intern side
from .models import InternshipPosting, Application
from users.models import Profile  # adjust if different app

def get_top_matches(intern_profile: Profile, limit: int = 6, min_score: float = 60.0):
    """
    Returns top matching active postings for the given intern profile.
    Returns list of tuples: (posting, match_score)
    """
    active_postings = InternshipPosting.objects.filter(is_active=True)
    
    scored = []
    for posting in active_postings:
        score = calculate_match_score(intern_profile, posting)  # your existing function
        if score >= min_score:
            scored.append((posting, score))
    
    # Sort descending by score
    scored.sort(key=lambda x: x[1], reverse=True)
    
    return scored[:limit]