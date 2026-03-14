from django.urls import path
from . import views

app_name = 'internships'

urlpatterns = [
    path('create/', views.create_posting, name='create_posting'),
    path('posting/<int:pk>/applications/', views.view_posting_applications, name='view_posting_applications'),
    path('application/<int:pk>/update-status/', views.update_application_status, name='update_application_status'),
    path('candidates/', views.view_candidates, name='view_candidates'),
    path('posting/<int:pk>/manage-applications/', views.manage_applications, name='manage_applications'),
    path('application/<int:application_id>/update-status/', views.update_application_status, name='update_application_status'),
]