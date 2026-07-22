from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .services import DashboardService
from users.models import CustomUser
from users.rbac import redirect_to_role_dashboard, role_required


DASHBOARD_TEMPLATES = {
    CustomUser.Role.SUPER_ADMIN: 'core/dashboards/super_admin.html',
    CustomUser.Role.SCHOOL_ADMIN: 'core/dashboards/school_admin.html',
    CustomUser.Role.TEACHER: 'core/dashboards/teacher.html',
    CustomUser.Role.STUDENT: 'core/dashboards/student.html',
    CustomUser.Role.PARENT: 'core/dashboards/parent.html',
    CustomUser.Role.COUNSELOR: 'core/dashboards/counselor.html',
    CustomUser.Role.LIBRARIAN: 'core/dashboards/librarian.html',
    CustomUser.Role.HOSTEL_STAFF: 'core/dashboards/hostel_staff.html',
}


def landing(request):
    if request.user.is_authenticated:
        return redirect_to_role_dashboard(request.user)
    return render(request, 'core/landing.html')


@login_required
def dashboard(request):
    return redirect_to_role_dashboard(request.user)


def render_dashboard(request, role):
    dashboard_data = DashboardService.for_user(request.user, getattr(request, 'school', None))
    return render(request, DASHBOARD_TEMPLATES[role], {'dashboard_data': dashboard_data})

@role_required(CustomUser.Role.SUPER_ADMIN)
def super_admin_dashboard(request):
    return render_dashboard(request, CustomUser.Role.SUPER_ADMIN)


@role_required(CustomUser.Role.SCHOOL_ADMIN)
def school_admin_dashboard(request):
    return render_dashboard(request, CustomUser.Role.SCHOOL_ADMIN)


@role_required(CustomUser.Role.TEACHER)
def teacher_dashboard(request):
    return render_dashboard(request, CustomUser.Role.TEACHER)


@role_required(CustomUser.Role.STUDENT)
def student_dashboard(request):
    return render_dashboard(request, CustomUser.Role.STUDENT)


@role_required(CustomUser.Role.PARENT)
def parent_dashboard(request):
    return render_dashboard(request, CustomUser.Role.PARENT)


@role_required(CustomUser.Role.COUNSELOR)
def counselor_dashboard(request):
    return render_dashboard(request, CustomUser.Role.COUNSELOR)


@role_required(CustomUser.Role.LIBRARIAN)
def librarian_dashboard(request):
    return render_dashboard(request, CustomUser.Role.LIBRARIAN)


@role_required(CustomUser.Role.HOSTEL_STAFF)
def hostel_staff_dashboard(request):
    return render_dashboard(request, CustomUser.Role.HOSTEL_STAFF)
