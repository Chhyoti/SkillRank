from django.urls import path, include

from applications import views
from .views import home, RegisterView, CustomLoginView, CustomLogoutView, employer_dashboard, intern_dashboard
from users import views

app_name = 'users'

urlpatterns = [
    path('', home, name='home'),  # ← empty path = homepage
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('employer/dashboard/', employer_dashboard, name='employer_dashboard'),
    path('intern/dashboard/', intern_dashboard, name='intern_dashboard'),
    path('intern/profile/<int:profile_id>/', views.view_intern_profile, name='view_intern_profile'),
    path('intern/profile/edit/', views.edit_intern_profile, name='edit_intern_profile'),
]