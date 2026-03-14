from django.urls import path
from . import views

app_name = 'skills'

urlpatterns = [
    path('add/', views.add_skill, name='add_skill'),
    path('remove/<int:pk>/', views.remove_skill, name='remove_skill'),
]