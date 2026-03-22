# from django.urls import path
# from . import views

# app_name = 'internships'

# urlpatterns = [
#     path('create/', views.create_posting, name='create_posting'),
#     path('posting/<int:pk>/applications/', views.view_posting_applications, name='view_posting_applications'),
#     path('application/<int:pk>/update-status/', views.update_application_status, name='update_application_status'),
#     path('candidates/', views.view_candidates, name='view_candidates'),
#     # path('posting/<int:pk>/manage-applications/', views.manage_applications, name='manage_applications'),
#     path('application/<int:application_id>/update-status/', views.update_application_status, name='update_application_status'),
#     #path('applications/manage/', views.manage_all_applications, name='manage_all_applications'),
#     path('top-matches/', views.view_top_matches, name='view_top_matches'),
# ]

from django.urls import path
from . import views

app_name = 'internships'

urlpatterns = [
    # Create new posting
    path('create/', views.create_posting, name='create_posting'),

    # The only candidates page — ranking + status change
    path('candidates/', views.view_candidates, name='view_candidates'),

    # Status update (called from candidates page)
    path('application/<int:application_id>/update-status/', views.update_application_status, name='update_application_status'),
    path('posting/<int:pk>/applications/', views.view_posting_applications, name='view_posting_applications'),
    path('browse/', views.browse_postings, name='browse_postings'),
    path('apply/<int:posting_id>/', views.apply_to_posting, name='apply_to_posting'),
    path('my-applications/', views.my_applications, name='my_applications'),
]