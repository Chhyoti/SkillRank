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

def get_ranked_candidates(employer_profile, limit=None):
    my_postings = employer_profile.postings.filter(is_active=True)

    if not my_postings.exists():
        return []

    applications = Application.objects.filter(posting__in=my_postings)

    interns = set(app.intern for app in applications)

    candidate_list = []

    for intern in interns:
        intern_apps = applications.filter(intern=intern)

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

    # candidate_list.sort(key=lambda x: x['highest_score'], reverse=True)
    candidate_list.sort(
    key=lambda x: (
        -x['highest_score'],               # Primary: higher score first (negative for descending)
        -x['application_count'],           # Secondary: more applications first
        x['intern'].user.username.lower()  # Tertiary: alphabetical by username (case-insensitive)
    )
)

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