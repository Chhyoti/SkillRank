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