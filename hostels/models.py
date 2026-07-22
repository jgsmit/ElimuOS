from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils import timezone


class Hostel(models.Model):
    school = models.ForeignKey('schools.School', on_delete=models.CASCADE, related_name='hostels')
    name = models.CharField(max_length=160)
    description = models.TextField(blank=True)
    warden = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name='managed_hostels', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        constraints = [models.UniqueConstraint(fields=['school', 'name'], name='unique_hostel_name_per_school')]

    @property
    def capacity(self):
        return sum(room.capacity for room in self.rooms.all())

    @property
    def occupancy(self):
        return sum(room.occupancy for room in self.rooms.all())

    @property
    def available_spaces(self):
        return max(self.capacity - self.occupancy, 0)

    def __str__(self):
        return f'{self.school} - {self.name}'


class Room(models.Model):
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name='rooms')
    room_number = models.CharField(max_length=40)
    floor = models.CharField(max_length=40, blank=True)
    capacity = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['hostel__name', 'room_number']
        constraints = [models.UniqueConstraint(fields=['hostel', 'room_number'], name='unique_room_number_per_hostel')]

    @property
    def occupancy(self):
        return self.allocations.filter(is_active=True).count()

    @property
    def available_spaces(self):
        return max(self.capacity - self.occupancy, 0)

    @property
    def is_full(self):
        return self.available_spaces == 0

    def clean(self):
        if self.capacity < 1:
            raise ValidationError({'capacity': 'Room capacity must be at least one.'})
        if self.pk and self.capacity < self.occupancy:
            raise ValidationError({'capacity': 'Capacity cannot be below current active occupancy.'})

    def __str__(self):
        return f'{self.hostel.name} - {self.room_number}'


class RoomAllocation(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='room_allocations')
    room = models.ForeignKey(Room, on_delete=models.PROTECT, related_name='allocations')
    session = models.ForeignKey('academics.AcademicSession', on_delete=models.PROTECT, related_name='room_allocations')
    allocated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name='created_room_allocations', blank=True, null=True)
    allocated_at = models.DateTimeField(default=timezone.now)
    released_at = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['room', 'student__username']
        constraints = [
            models.UniqueConstraint(fields=['student', 'session'], condition=Q(is_active=True), name='unique_active_room_allocation_per_student_session'),
        ]

    def clean(self):
        if self.student.role != self.student.Role.STUDENT:
            raise ValidationError({'student': 'Only students can be allocated hostel rooms.'})
        if self.student.school_id and self.student.school_id != self.room.hostel.school_id:
            raise ValidationError({'student': 'Student must belong to the same school as the hostel.'})
        if self.session.school_id != self.room.hostel.school_id:
            raise ValidationError({'session': 'Academic session must belong to the same school as the hostel.'})
        if self.is_active and self.room.is_full and not self.pk:
            raise ValidationError({'room': 'Room capacity has been reached.'})
        if self.released_at and self.released_at < self.allocated_at:
            raise ValidationError({'released_at': 'Release time cannot be before allocation time.'})

    def release(self):
        self.is_active = False
        self.released_at = timezone.now()
        self.save(update_fields=['is_active', 'released_at'])

    def save(self, *args, **kwargs):
        if self.released_at:
            self.is_active = False
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.student} -> {self.room} ({self.session})'


class VisitorLog(models.Model):
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name='visitor_logs')
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name='hostel_visitors', blank=True, null=True)
    visitor_name = models.CharField(max_length=160)
    visitor_phone = models.CharField(max_length=32, blank=True)
    purpose = models.CharField(max_length=255)
    checked_in_at = models.DateTimeField(default=timezone.now)
    checked_out_at = models.DateTimeField(blank=True, null=True)
    recorded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name='recorded_hostel_visitors', blank=True, null=True)

    class Meta:
        ordering = ['-checked_in_at']

    def clean(self):
        if self.student and self.student.school_id and self.student.school_id != self.hostel.school_id:
            raise ValidationError({'student': 'Visited student must belong to the same school as the hostel.'})
        if self.checked_out_at and self.checked_out_at < self.checked_in_at:
            raise ValidationError({'checked_out_at': 'Checkout time cannot be before check-in time.'})

    def checkout(self):
        self.checked_out_at = timezone.now()
        self.save(update_fields=['checked_out_at'])

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.visitor_name} at {self.hostel}'


class HostelExpense(models.Model):
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name='expenses')
    category = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    expense_date = models.DateField(default=timezone.localdate)
    recorded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name='recorded_hostel_expenses', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-expense_date', 'category']

    def clean(self):
        if self.amount <= 0:
            raise ValidationError({'amount': 'Expense amount must be greater than zero.'})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.hostel} - {self.category} - {self.amount}'
