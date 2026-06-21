from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing, name='landing'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/super-admin/', views.super_admin_dashboard, name='dashboard_super_admin'),
    path('dashboard/school-admin/', views.school_admin_dashboard, name='dashboard_school_admin'),
    path('dashboard/teacher/', views.teacher_dashboard, name='dashboard_teacher'),
    path('dashboard/student/', views.student_dashboard, name='dashboard_student'),
    path('dashboard/parent/', views.parent_dashboard, name='dashboard_parent'),
    path('dashboard/counselor/', views.counselor_dashboard, name='dashboard_counselor'),
    path('dashboard/librarian/', views.librarian_dashboard, name='dashboard_librarian'),
    path('dashboard/hostel-staff/', views.hostel_staff_dashboard, name='dashboard_hostel_staff'),
]
