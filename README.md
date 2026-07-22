# ElimuOS / Shule Yangu

A phased Django school management system.

## Phase 1: Project Foundation

Implemented:

- Django project structure (`shule_yangu`)
- Environment-based settings via `python-decouple`
- SQLite development database with PostgreSQL-ready environment variables
- WhiteNoise static file support
- Africa/Nairobi timezone
- Bootstrap 5 base templates
- Initial `core` and `users` apps
- Custom swappable user model
- Login/logout routes and templates

## Setup

```bash
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Phase 2: Authentication & RBAC

Implemented:

- Strict role choices for super admin, school admin, teacher, student, parent, counselor, librarian, and hostel staff
- User profile fields for phone, address, and profile picture
- Automatic staff/student identifier generation
- Login history and active session tracking
- RBAC decorator and class-based-view mixin
- Role-based login redirects and placeholder dashboards

## Phase 3: Multi-Tenant Architecture

Implemented:

- `schools` app with `School` tenants and one-to-one `SchoolBranding`
- Hostname-based tenant resolution with optional `?school=<slug>` development fallback
- Tenant middleware that attaches `request.school` / `request.tenant`
- Template context injection for tenant branding
- Tenant-aware navigation and role dashboard placeholders

## Phase 4: Core School Module

Implemented:

- Academic sessions with one active session per school
- School classes with capacity tracking
- Subjects and class-subject teacher assignments
- Student enrollments with automatic roll number generation
- Timetable entries
- Basic attendance tracking

## Phase 5: Examination System

Implemented:

- Exam types and exams with weighted grading support
- MCQ question and choice bank foundations
- Result entry with automatic percentage and grade calculation
- Grading systems with non-overlapping grade bands
- Continuous assessment tracking
- Report card generation with weighted subject and overall summaries

## Phase 6: Library System

Implemented:

- Tenant-scoped book categories, authors, and publishers
- Book inventory with total-copy and dynamic availability tracking
- Borrow/return workflow with active borrowing constraints
- Fine calculation for overdue returns
- Admin and tests for inventory, borrowing, return, and fine behavior

## Phase 7: Hostel System

Implemented:

- Tenant-scoped hostels and rooms with dynamic occupancy tracking
- Student room allocation workflow with one active allocation per student per session
- Room capacity enforcement and allocation release workflow
- Visitor logs with check-in/checkout timestamps
- Hostel expense tracking with validation

## Phase 8: Communication System

Implemented:

- Direct, class, and role-group internal messages
- Message receipts with delivered/read tracking
- Announcements with priority, role/class targeting, publish/expiry windows
- Announcement receipts with read tracking
- Admin and tests for messaging, class announcements, and read receipts

## Phase 9: Dashboards & Reporting

Implemented:

- Role-aware `DashboardService` for super admin, school admin, teacher, student, parent, counselor, librarian, and hostel staff
- Aggregated dashboard metrics, summary insights, and chart-ready datasets
- Role dashboard templates upgraded from placeholders to functional reporting views
- Tests covering dashboard aggregation for school admins, teachers, and students

## Phase 10: Security & Polish

Implemented:

- Audit logs for authenticated write requests
- Privacy redaction helpers for sensitive metadata
- Session timeout middleware
- Security hardening settings for cookies, HTTPS readiness, HSTS, content sniffing, and frame options
- User profile/admin form validation polish
