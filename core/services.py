from django.utils import timezone

from academics.models import AcademicSession, Attendance, ClassSubject, SchoolClass, StudentEnrollment
from communications.models import Announcement, Message
from examinations.models import ReportCard, Result
from hostels.models import Hostel, HostelExpense, RoomAllocation
from library.models import Book, BookBorrowing
from schools.models import School
from users.models import CustomUser


class DashboardService:
    """Aggregate role-specific dashboard metrics for Shule Yangu."""

    @classmethod
    def for_user(cls, user, request_school=None):
        school = request_school or getattr(user, 'school', None)
        if user.role == CustomUser.Role.SUPER_ADMIN:
            return cls.super_admin()
        if user.role == CustomUser.Role.SCHOOL_ADMIN:
            return cls.school_admin(school)
        if user.role == CustomUser.Role.TEACHER:
            return cls.teacher(user, school)
        if user.role == CustomUser.Role.STUDENT:
            return cls.student(user, school)
        if user.role == CustomUser.Role.PARENT:
            return cls.parent(user, school)
        if user.role == CustomUser.Role.COUNSELOR:
            return cls.counselor(school)
        if user.role == CustomUser.Role.LIBRARIAN:
            return cls.librarian(school)
        if user.role == CustomUser.Role.HOSTEL_STAFF:
            return cls.hostel_staff(school)
        return cls.empty('Dashboard')

    @staticmethod
    def empty(title):
        return {'title': title, 'metrics': [], 'charts': [], 'summaries': []}

    @staticmethod
    def metric(label, value, hint=''):
        return {'label': label, 'value': value, 'hint': hint}

    @staticmethod
    def chart(label, labels, values):
        return {'label': label, 'points': [{'label': item_label, 'value': item_value} for item_label, item_value in zip(labels, values)]}

    @classmethod
    def super_admin(cls):
        return {
            'title': 'Super Admin Overview',
            'metrics': [
                cls.metric('Schools', School.objects.count(), 'All tenant schools'),
                cls.metric('Users', CustomUser.objects.count(), 'All platform users'),
                cls.metric('Active Sessions', AcademicSession.objects.filter(is_active=True).count(), 'Across all schools'),
                cls.metric('Library Books', Book.objects.count(), 'All catalogued books'),
            ],
            'charts': [
                cls.chart('Users by role', *cls._role_chart(CustomUser.objects.all())),
            ],
            'summaries': ['Platform-wide snapshot across all tenants.'],
        }

    @classmethod
    def school_admin(cls, school):
        if not school:
            return cls.empty('School Admin Dashboard')
        users = CustomUser.objects.filter(school=school)
        return {
            'title': 'School Admin Dashboard',
            'metrics': [
                cls.metric('Students', users.filter(role=CustomUser.Role.STUDENT).count(), 'Active student accounts'),
                cls.metric('Teachers', users.filter(role=CustomUser.Role.TEACHER).count(), 'Teaching staff'),
                cls.metric('Classes', SchoolClass.objects.filter(school=school).count(), 'Configured classes'),
                cls.metric('Messages', Message.objects.filter(school=school).count(), 'Internal messages'),
            ],
            'charts': [cls.chart('Users by role', *cls._role_chart(users))],
            'summaries': [f'Operational overview for {school.name}.'],
        }

    @classmethod
    def teacher(cls, user, school):
        assignments = ClassSubject.objects.filter(teacher=user)
        class_ids = assignments.values_list('school_class_id', flat=True)
        return {
            'title': 'Teacher Class View',
            'metrics': [
                cls.metric('Subject Assignments', assignments.count(), 'Class-subject assignments'),
                cls.metric('Assigned Classes', SchoolClass.objects.filter(pk__in=class_ids).distinct().count(), 'Classes you teach'),
                cls.metric('Students', StudentEnrollment.objects.filter(school_class_id__in=class_ids, is_active=True).count(), 'Learners in assigned classes'),
                cls.metric('Results Recorded', Result.objects.filter(exam__created_by=user).count(), 'Exam results for your exams'),
            ],
            'charts': [cls.chart('Assigned subjects', ['Assignments', 'Classes'], [assignments.count(), SchoolClass.objects.filter(pk__in=class_ids).distinct().count()])],
            'summaries': ['Teaching workload and learner coverage.'],
        }

    @classmethod
    def student(cls, user, school):
        enrollments = StudentEnrollment.objects.filter(student=user, is_active=True)
        attendance = Attendance.objects.filter(enrollment__in=enrollments)
        present = attendance.filter(status=Attendance.Status.PRESENT).count()
        total_attendance = attendance.count()
        attendance_rate = round((present / total_attendance) * 100, 2) if total_attendance else 0
        results = Result.objects.filter(enrollment__in=enrollments)
        avg_score = cls._average_percentage(results)
        return {
            'title': 'Student Performance Dashboard',
            'metrics': [
                cls.metric('Active Enrollments', enrollments.count(), 'Current class/session records'),
                cls.metric('Attendance Rate', f'{attendance_rate}%', 'Present records over total records'),
                cls.metric('Average Score', f'{avg_score}%', 'Average exam percentage'),
                cls.metric('Borrowed Books', BookBorrowing.objects.filter(borrower=user, returned_at__isnull=True).count(), 'Currently borrowed'),
            ],
            'charts': [cls.chart('Performance snapshot', ['Attendance', 'Average Score'], [attendance_rate, avg_score])],
            'summaries': [f'{ReportCard.objects.filter(enrollment__in=enrollments).count()} report card(s) generated.'],
        }

    @classmethod
    def parent(cls, user, school):
        return {
            'title': 'Parent Dashboard',
            'metrics': [
                cls.metric('Messages', user.message_receipts.count(), 'Messages received'),
                cls.metric('Unread Messages', user.message_receipts.filter(read_at__isnull=True).count(), 'Messages awaiting review'),
                cls.metric('Announcements', user.announcement_receipts.count(), 'Announcements received'),
                cls.metric('Unread Announcements', user.announcement_receipts.filter(read_at__isnull=True).count(), 'Announcements awaiting review'),
            ],
            'charts': [cls.chart('Read tracking', ['Messages', 'Announcements'], [user.message_receipts.filter(read_at__isnull=False).count(), user.announcement_receipts.filter(read_at__isnull=False).count()])],
            'summaries': ['Parent-child linking will be expanded in a later student relations phase.'],
        }

    @classmethod
    def counselor(cls, school):
        enrollments = StudentEnrollment.objects.filter(school_class__school=school, is_active=True) if school else StudentEnrollment.objects.none()
        absences = Attendance.objects.filter(enrollment__in=enrollments, status=Attendance.Status.ABSENT).count()
        return {
            'title': 'Counselor Dashboard',
            'metrics': [
                cls.metric('Students', enrollments.count(), 'Active enrolled students'),
                cls.metric('Absence Flags', absences, 'Absent attendance records'),
                cls.metric('Late Flags', Attendance.objects.filter(enrollment__in=enrollments, status=Attendance.Status.LATE).count(), 'Late attendance records'),
                cls.metric('Announcements', Announcement.objects.filter(school=school).count() if school else 0, 'School announcements'),
            ],
            'charts': [cls.chart('Student wellbeing flags', ['Absent', 'Late'], [absences, Attendance.objects.filter(enrollment__in=enrollments, status=Attendance.Status.LATE).count()])],
            'summaries': ['Counseling alerts based on attendance patterns.'],
        }

    @classmethod
    def librarian(cls, school):
        today = timezone.localdate()
        borrowings = BookBorrowing.objects.filter(book__school=school) if school else BookBorrowing.objects.none()
        return {
            'title': 'Librarian Dashboard',
            'metrics': [
                cls.metric('Books', Book.objects.filter(school=school).count() if school else 0, 'Catalogued books'),
                cls.metric('Active Borrowings', borrowings.filter(returned_at__isnull=True).count(), 'Currently borrowed'),
                cls.metric('Overdue', borrowings.filter(returned_at__isnull=True, due_date__lt=today).count(), 'Late returns'),
                cls.metric('Fines', borrowings.aggregate_total_fines() if hasattr(borrowings, 'aggregate_total_fines') else sum(b.fine_amount for b in borrowings), 'Recorded fine total'),
            ],
            'charts': [cls.chart('Borrowing status', ['Active', 'Overdue'], [borrowings.filter(returned_at__isnull=True).count(), borrowings.filter(returned_at__isnull=True, due_date__lt=today).count()])],
            'summaries': ['Library inventory and circulation snapshot.'],
        }

    @classmethod
    def hostel_staff(cls, school):
        hostels = Hostel.objects.filter(school=school) if school else Hostel.objects.none()
        allocations = RoomAllocation.objects.filter(room__hostel__school=school, is_active=True) if school else RoomAllocation.objects.none()
        expenses = HostelExpense.objects.filter(hostel__school=school) if school else HostelExpense.objects.none()
        capacity = sum(hostel.capacity for hostel in hostels)
        occupancy = allocations.count()
        return {
            'title': 'Hostel Staff Dashboard',
            'metrics': [
                cls.metric('Hostels', hostels.count(), 'Active and inactive hostels'),
                cls.metric('Capacity', capacity, 'Total room spaces'),
                cls.metric('Occupancy', occupancy, 'Active allocations'),
                cls.metric('Expenses', sum(expense.amount for expense in expenses), 'Recorded expense total'),
            ],
            'charts': [cls.chart('Hostel occupancy', ['Occupied', 'Available'], [occupancy, max(capacity - occupancy, 0)])],
            'summaries': ['Accommodation capacity and expense overview.'],
        }

    @staticmethod
    def _role_chart(users):
        labels, values = [], []
        for role, label in CustomUser.Role.choices:
            labels.append(label)
            values.append(users.filter(role=role).count())
        return labels, values

    @staticmethod
    def _average_percentage(results):
        values = list(results.values_list('percentage', flat=True))
        if not values:
            return 0
        return round(sum(values) / len(values), 2)
